import type { HealthDayResponse } from '../api/health_service';

export type HealthMetric = 'sleep' | 'hrv' | 'restingHr';
export type HealthRange = 7 | 30 | 90;

export interface HealthChartPoint {
  x: Date;
  y: number | null; // null = no reading that day; Victory breaks the line there
}

export interface HealthChartData {
  points: HealthChartPoint[]; // one per day in range, oldest first
  symptomDays: Date[]; // days in range with at least one symptom log
  hasMetricData: boolean; // false when every point in range is null
  domain: { x: [Date, Date]; y: [number, number] };
}

/** Local-calendar YYYY-MM-DD for a Date (not UTC, so it matches the user's day). */
export function toDayKey(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

/** Parse YYYY-MM-DD as local midnight (new Date('YYYY-MM-DD') would be UTC). */
export function parseDayKey(day: string): Date {
  const [y, m, d] = day.split('-').map(Number);
  return new Date(y, m - 1, d);
}

/** The [start, end] day keys for the last `rangeDays` days ending on `end`, inclusive. */
export function rangeBounds(end: string, rangeDays: number): { start: string; end: string } {
  const start = parseDayKey(end);
  start.setDate(start.getDate() - (rangeDays - 1));
  return { start: toDayKey(start), end };
}

function metricValue(day: HealthDayResponse, metric: HealthMetric): number | null {
  switch (metric) {
    case 'sleep':
      return day.sleep_total_min == null ? null : Math.round((day.sleep_total_min / 60) * 10) / 10;
    case 'hrv':
      return day.hrv_avg_ms;
    case 'restingHr':
      return day.resting_hr_bpm;
  }
}

/** True if any day has any metric — drives the "no health data yet" empty state. */
export function hasAnyHealthData(days: HealthDayResponse[]): boolean {
  return days.some((d) => d.sleep_total_min != null || d.hrv_avg_ms != null || d.resting_hr_bpm != null);
}

function yDomain(values: number[]): [number, number] {
  if (values.length === 0) return [0, 1];
  const min = Math.min(...values);
  const max = Math.max(...values);
  const pad = Math.max((max - min) * 0.15, max * 0.05, 1);
  return [Math.max(0, Math.floor(min - pad)), Math.ceil(max + pad)];
}

/**
 * Turns the /health/trends response into one chart series for `metric` over the last
 * `rangeDays` days ending on `end`. Every day in range gets a point; days the API omits or
 * returns without a reading become null so the line breaks instead of dropping to 0.
 */
export function buildHealthChartData(
  days: HealthDayResponse[],
  metric: HealthMetric,
  rangeDays: HealthRange,
  end: string,
): HealthChartData {
  const byDate = new Map(days.map((d) => [d.date, d]));
  const { start } = rangeBounds(end, rangeDays);

  const points: HealthChartPoint[] = [];
  const symptomDays: Date[] = [];
  const cursor = parseDayKey(start);
  for (let i = 0; i < rangeDays; i++) {
    const x = new Date(cursor);
    const day = byDate.get(toDayKey(x));
    points.push({ x, y: day ? metricValue(day, metric) : null });
    if (day && day.symptom_count > 0) symptomDays.push(x);
    cursor.setDate(cursor.getDate() + 1);
  }

  const values = points.map((p) => p.y).filter((y): y is number => y !== null);

  return {
    points,
    symptomDays,
    hasMetricData: values.length > 0,
    domain: { x: [parseDayKey(start), parseDayKey(end)], y: yDomain(values) },
  };
}

export type BreakdownBandKey = 'band0' | 'band1' | 'band2' | 'band3' | 'noData';

export interface BreakdownBand {
  key: BreakdownBandKey; // band0 = lowest values ... band3 = highest
  label: string;
  count: number;
}

export interface MetricBreakdown {
  bands: BreakdownBand[]; // fixed order, zero counts included
  daysTracked: number; // days with a reading for this metric
  totalDays: number; // = rangeDays
}

// Upper bounds are exclusive, so a value exactly on a boundary falls in the higher band.
// Sleep bounds are in minutes (raw sleep_total_min), HRV in ms, resting HR in bpm.
const BREAKDOWN_BANDS: Record<HealthMetric, { label: string; below: number }[]> = {
  sleep: [
    { label: 'Under 6h', below: 360 },
    { label: '6–7h', below: 420 },
    { label: '7–8h', below: 480 },
    { label: '8h+', below: Infinity },
  ],
  hrv: [
    { label: 'Under 30 ms', below: 30 },
    { label: '30–45 ms', below: 45 },
    { label: '45–60 ms', below: 60 },
    { label: '60+ ms', below: Infinity },
  ],
  restingHr: [
    { label: 'Under 55 bpm', below: 55 },
    { label: '55–65 bpm', below: 65 },
    { label: '65–75 bpm', below: 75 },
    { label: '75+ bpm', below: Infinity },
  ],
};

function rawMetricValue(day: HealthDayResponse, metric: HealthMetric): number | null {
  if (metric === 'sleep') return day.sleep_total_min;
  return metric === 'hrv' ? day.hrv_avg_ms : day.resting_hr_bpm;
}

/**
 * Groups the days in the last `rangeDays` days ending on `end` into value bands for `metric`.
 * Days without a reading count as "No data", so the bands always add up to the whole range.
 */
export function buildMetricBreakdown(
  days: HealthDayResponse[],
  metric: HealthMetric,
  rangeDays: HealthRange,
  end: string,
): MetricBreakdown {
  const byDate = new Map(days.map((d) => [d.date, d]));
  const { start } = rangeBounds(end, rangeDays);
  const config = BREAKDOWN_BANDS[metric];
  const counts = [0, 0, 0, 0];
  let noData = 0;

  const cursor = parseDayKey(start);
  for (let i = 0; i < rangeDays; i++) {
    const day = byDate.get(toDayKey(cursor));
    const value = day ? rawMetricValue(day, metric) : null;
    if (value == null) {
      noData += 1;
    } else {
      counts[config.findIndex((b) => value < b.below)] += 1;
    }
    cursor.setDate(cursor.getDate() + 1);
  }

  return {
    bands: [
      ...config.map((b, i) => ({ key: `band${i}` as BreakdownBandKey, label: b.label, count: counts[i] })),
      { key: 'noData', label: 'No data', count: noData },
    ],
    daysTracked: rangeDays - noData,
    totalDays: rangeDays,
  };
}
