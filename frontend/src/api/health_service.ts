import { apiClient, ApiError } from './client';

export interface HealthDayResponse {
  date: string; // YYYY-MM-DD, bucketed in the client timezone at sync time
  sleep_total_min: number | null;
  sleep_deep_min: number | null;
  sleep_rem_min: number | null;
  sleep_core_min: number | null;
  sleep_awake_min: number | null;
  hrv_avg_ms: number | null;
  resting_hr_bpm: number | null;
}

export const healthService = {

  // get_my_health_days()
  // NOTE: backend currently only exposes POST /health/sync; this GET endpoint still needs to be added.
  async getMyHealthDays(start: string, end: string): Promise<HealthDayResponse[]> {
    try {
      const { data } = await apiClient.get<HealthDayResponse[]>('/health/days', {
        params: { start, end },
      });
      return data;
    } catch (err: any) {
      throw new ApiError(err.response?.data?.detail ?? 'Failed to fetch health data');
    }
  },
};

// ---------------------------------------------------------------------------
// Chart transform
// ---------------------------------------------------------------------------

export type HealthMetricKey = 'sleep' | 'hrv' | 'restingHr';

export interface HealthTrendPoint {
  x: Date;
  y: number | null; // null = no reading that day; Victory renders it as a gap
}

export interface HealthTrends {
  days: string[]; // every YYYY-MM-DD in [start, end], inclusive
  series: Record<HealthMetricKey, HealthTrendPoint[]>;
  symptomDays: string[]; // days in range with at least one symptom log
  hasData: Record<HealthMetricKey, boolean>;
}

interface SymptomLogLike {
  timestamp: string;
}

/** Local-calendar YYYY-MM-DD for a Date (not UTC, so late-evening logs land on the right day). */
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

function eachDay(start: string, end: string): string[] {
  const days: string[] = [];
  const cursor = parseDayKey(start);
  const last = parseDayKey(end);
  while (cursor <= last) {
    days.push(toDayKey(cursor));
    cursor.setDate(cursor.getDate() + 1);
  }
  return days;
}

/**
 * Lines up daily health metrics and symptom logs on one daily timeline.
 * Sleep is converted from minutes to hours; days without a reading become null gaps.
 */
export function buildHealthTrends(
  healthDays: HealthDayResponse[],
  symptomLogs: SymptomLogLike[],
  start: string,
  end: string,
): HealthTrends {
  const days = eachDay(start, end);
  const byDate = new Map(healthDays.map((d) => [d.date, d]));

  const pick = (fn: (d: HealthDayResponse) => number | null): HealthTrendPoint[] =>
    days.map((day) => {
      const entry = byDate.get(day);
      const value = entry ? fn(entry) : null;
      return { x: parseDayKey(day), y: value ?? null };
    });

  const series: Record<HealthMetricKey, HealthTrendPoint[]> = {
    sleep: pick((d) => (d.sleep_total_min == null ? null : Math.round((d.sleep_total_min / 60) * 10) / 10)),
    hrv: pick((d) => d.hrv_avg_ms),
    restingHr: pick((d) => d.resting_hr_bpm),
  };

  const inRange = new Set(days);
  const symptomDays = Array.from(
    new Set(symptomLogs.map((log) => toDayKey(new Date(log.timestamp))).filter((day) => inRange.has(day))),
  ).sort();

  const hasData = {
    sleep: series.sleep.some((p) => p.y !== null),
    hrv: series.hrv.some((p) => p.y !== null),
    restingHr: series.restingHr.some((p) => p.y !== null),
  };

  return { days, series, symptomDays, hasData };
}

export interface MetricSummary {
  symptomDayAvg: number | null;
  otherDayAvg: number | null;
}

function average(values: number[]): number | null {
  if (values.length === 0) return null;
  return Math.round((values.reduce((a, b) => a + b, 0) / values.length) * 10) / 10;
}

/** Average of a metric on symptom days vs. all other days that have a reading. */
export function summarizeMetric(points: HealthTrendPoint[], symptomDays: string[]): MetricSummary {
  const symptomSet = new Set(symptomDays);
  const onSymptomDays: number[] = [];
  const otherDays: number[] = [];
  for (const p of points) {
    if (p.y === null) continue;
    (symptomSet.has(toDayKey(p.x)) ? onSymptomDays : otherDays).push(p.y);
  }
  return { symptomDayAvg: average(onSymptomDays), otherDayAvg: average(otherDays) };
}
