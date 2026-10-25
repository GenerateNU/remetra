import type { HealthDayResponse } from '../../api/health_service';
import {
  buildHealthChartData,
  buildMetricBreakdown,
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

describe('buildMetricBreakdown', () => {
  const countsOf = (b: ReturnType<typeof buildMetricBreakdown>) =>
    Object.fromEntries(b.bands.map((x) => [x.label, x.count]));

  test('groups sleep by length; a night exactly on a boundary goes in the higher band', () => {
    const breakdown = buildMetricBreakdown(
      [
        day('2026-10-01', { sleep_total_min: 359 }),
        day('2026-10-02', { sleep_total_min: 360 }), // exactly 6h
        day('2026-10-03', { sleep_total_min: 419 }),
        day('2026-10-04', { sleep_total_min: 420 }), // exactly 7h
        day('2026-10-05', { sleep_total_min: 480 }), // exactly 8h
        day('2026-10-06', { sleep_total_min: 655 }),
      ],
      'sleep',
      7,
      '2026-10-07',
    );

    expect(countsOf(breakdown)).toEqual({ 'Under 6h': 1, '6–7h': 2, '7–8h': 1, '8h+': 2, 'No data': 1 });
  });

  test('groups HRV into ms bands', () => {
    const breakdown = buildMetricBreakdown(
      [
        day('2026-10-04', { hrv_avg_ms: 19.5 }),
        day('2026-10-05', { hrv_avg_ms: 30 }),
        day('2026-10-06', { hrv_avg_ms: 59.9 }),
        day('2026-10-07', { hrv_avg_ms: 72 }),
      ],
      'hrv',
      7,
      '2026-10-07',
    );

    expect(countsOf(breakdown)).toEqual({
      'Under 30 ms': 1, '30–45 ms': 1, '45–60 ms': 1, '60+ ms': 1, 'No data': 3,
    });
  });

  test('groups resting HR into bpm bands', () => {
    const breakdown = buildMetricBreakdown(
      [
        day('2026-10-05', { resting_hr_bpm: 54.9 }),
        day('2026-10-06', { resting_hr_bpm: 65 }),
        day('2026-10-07', { resting_hr_bpm: 84 }),
      ],
      'restingHr',
      7,
      '2026-10-07',
    );

    expect(countsOf(breakdown)).toEqual({
      'Under 55 bpm': 1, '55–65 bpm': 0, '65–75 bpm': 1, '75+ bpm': 1, 'No data': 4,
    });
  });

  test('bands always add up to the whole range', () => {
    const breakdown = buildMetricBreakdown([day('2026-10-07', { sleep_total_min: 450 })], 'sleep', 30, '2026-10-07');

    expect(breakdown.totalDays).toBe(30);
    expect(breakdown.bands.reduce((sum, b) => sum + b.count, 0)).toBe(30);
    expect(breakdown.daysTracked).toBe(1);
  });

  test('a day missing one metric counts as no data for that metric only', () => {
    const days = [day('2026-10-07', { hrv_avg_ms: 40, resting_hr_bpm: 60, symptom_count: 2 })];

    expect(buildMetricBreakdown(days, 'sleep', 7, '2026-10-07').daysTracked).toBe(0);
    expect(buildMetricBreakdown(days, 'hrv', 7, '2026-10-07').daysTracked).toBe(1);
  });

  test('ignores days outside the range', () => {
    const breakdown = buildMetricBreakdown([day('2026-09-01', { hrv_avg_ms: 40 })], 'hrv', 7, '2026-10-07');

    expect(breakdown.daysTracked).toBe(0);
  });

  test('keeps a fixed band order with zero counts, so colors stay attached to each band', () => {
    const breakdown = buildMetricBreakdown([], 'restingHr', 7, '2026-10-07');

    expect(breakdown.bands.map((b) => b.key)).toEqual(['band0', 'band1', 'band2', 'band3', 'noData']);
  });
});
