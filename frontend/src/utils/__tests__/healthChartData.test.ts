import type { HealthDayResponse } from '../../api/health_service';
import {
  buildHealthChartData,
  hasAnyHealthData,
  parseDayKey,
  rangeBounds,
  toDayKey,
} from '../healthChartData';

function day(date: string, overrides: Partial<HealthDayResponse> = {}): HealthDayResponse {
  return {
    date,
    sleep_total_min: null,
    hrv_avg_ms: null,
    resting_hr_bpm: null,
    symptom_count: 0,
    max_intensity: null,
    ...overrides,
  };
}

const keys = (dates: Date[]) => dates.map(toDayKey);

test('null values produce a line break, not a 0 point', () => {
  const data = buildHealthChartData(
    [
      day('2026-10-05', { hrv_avg_ms: 40 }),
      day('2026-10-06'), // returned by the API with null metrics
      day('2026-10-07', { hrv_avg_ms: 44 }),
    ],
    'hrv',
    7,
    '2026-10-07',
  );

  expect(data.points.map((p) => p.y)).toEqual([null, null, null, null, 40, null, 44]);
  expect(data.points.some((p) => p.y === 0)).toBe(false);
});

test('a 7-day range with data on 3 days gives 7 points, 4 of them null', () => {
  const data = buildHealthChartData(
    [
      day('2026-10-01', { sleep_total_min: 420 }),
      day('2026-10-03', { sleep_total_min: 390 }),
      day('2026-10-07', { sleep_total_min: 480 }),
    ],
    'sleep',
    7,
    '2026-10-07',
  );

  expect(keys(data.points.map((p) => p.x))).toEqual([
    '2026-10-01', '2026-10-02', '2026-10-03', '2026-10-04', '2026-10-05', '2026-10-06', '2026-10-07',
  ]);
  expect(data.points.filter((p) => p.y === null)).toHaveLength(4);
});

test('converts sleep minutes to hours, rounded to one decimal', () => {
  const data = buildHealthChartData([day('2026-10-07', { sleep_total_min: 437 })], 'sleep', 7, '2026-10-07');

  expect(data.points[6].y).toBe(7.3);
});

test('picks the selected metric', () => {
  const days = [day('2026-10-07', { sleep_total_min: 420, hrv_avg_ms: 45.5, resting_hr_bpm: 58 })];

  expect(buildHealthChartData(days, 'hrv', 7, '2026-10-07').points[6].y).toBe(45.5);
  expect(buildHealthChartData(days, 'restingHr', 7, '2026-10-07').points[6].y).toBe(58);
});

test('range toggle slices the last N days ending on end', () => {
  const days = [day('2026-07-20', { hrv_avg_ms: 50 }), day('2026-10-07', { hrv_avg_ms: 45 })];

  const week = buildHealthChartData(days, 'hrv', 7, '2026-10-07');
  const quarter = buildHealthChartData(days, 'hrv', 90, '2026-10-07');

  expect(week.points).toHaveLength(7);
  expect(quarter.points).toHaveLength(90);
  expect(toDayKey(quarter.points[0].x)).toBe('2026-07-10');
  expect(quarter.points.filter((p) => p.y !== null)).toHaveLength(2);
  expect(week.points.filter((p) => p.y !== null)).toHaveLength(1);
});

test('days missing from the response are treated as gaps', () => {
  const data = buildHealthChartData([], 'restingHr', 7, '2026-10-07');

  expect(data.points).toHaveLength(7);
  expect(data.points.every((p) => p.y === null)).toBe(true);
  expect(data.hasMetricData).toBe(false);
});

test('marks symptom days from symptom_count, including days with no health data', () => {
  const data = buildHealthChartData(
    [
      day('2026-10-02', { symptom_count: 2, max_intensity: 6, hrv_avg_ms: 30 }),
      day('2026-10-04', { symptom_count: 1, max_intensity: 3 }), // no metrics that day
      day('2026-10-05', { hrv_avg_ms: 48 }),
      day('2026-09-20', { symptom_count: 1, max_intensity: 5 }), // outside the range
    ],
    'hrv',
    7,
    '2026-10-07',
  );

  expect(keys(data.symptomDays)).toEqual(['2026-10-02', '2026-10-04']);
});

test('hasMetricData is per metric', () => {
  const days = [day('2026-10-07', { resting_hr_bpm: 60 })];

  expect(buildHealthChartData(days, 'restingHr', 7, '2026-10-07').hasMetricData).toBe(true);
  expect(buildHealthChartData(days, 'sleep', 7, '2026-10-07').hasMetricData).toBe(false);
});

test('y domain pads around the data and never goes below 0', () => {
  const data = buildHealthChartData(
    [day('2026-10-06', { hrv_avg_ms: 20 }), day('2026-10-07', { hrv_avg_ms: 60 })],
    'hrv',
    7,
    '2026-10-07',
  );

  const [lo, hi] = data.domain.y;
  expect(lo).toBeLessThan(20);
  expect(lo).toBeGreaterThanOrEqual(0);
  expect(hi).toBeGreaterThan(60);
});

test('x domain spans the whole range even when the edges have no data', () => {
  const data = buildHealthChartData([day('2026-10-04', { hrv_avg_ms: 40 })], 'hrv', 7, '2026-10-07');

  expect(keys(data.domain.x)).toEqual(['2026-10-01', '2026-10-07']);
});

test('hasAnyHealthData ignores symptom-only days', () => {
  expect(hasAnyHealthData([day('2026-10-01', { symptom_count: 3, max_intensity: 7 })])).toBe(false);
  expect(hasAnyHealthData([day('2026-10-01', { hrv_avg_ms: 40 })])).toBe(true);
  expect(hasAnyHealthData([])).toBe(false);
});

test('rangeBounds crosses month boundaries and includes both ends', () => {
  expect(rangeBounds('2026-10-03', 7)).toEqual({ start: '2026-09-27', end: '2026-10-03' });
  expect(rangeBounds('2026-10-03', 1)).toEqual({ start: '2026-10-03', end: '2026-10-03' });
});

test('parseDayKey gives local midnight and round-trips with toDayKey', () => {
  const d = parseDayKey('2026-03-08'); // US DST change day
  expect(d.getHours()).toBe(0);
  expect(toDayKey(d)).toBe('2026-03-08');
});
