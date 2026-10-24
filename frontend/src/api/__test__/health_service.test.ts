import { buildHealthTrends, HealthDayResponse, toDayKey, parseDayKey, summarizeMetric } from '../health_service';

function day(date: string, overrides: Partial<HealthDayResponse> = {}): HealthDayResponse {
  return {
    date,
    sleep_total_min: null,
    sleep_deep_min: null,
    sleep_rem_min: null,
    sleep_core_min: null,
    sleep_awake_min: null,
    hrv_avg_ms: null,
    resting_hr_bpm: null,
    ...overrides,
  };
}

// Builds an ISO timestamp for a local wall-clock time, so tests pass in any TZ
function localIso(y: number, m: number, d: number, h = 12): string {
  return new Date(y, m - 1, d, h).toISOString();
}

test('produces one point per day in range, inclusive', () => {
  const trends = buildHealthTrends([], [], '2026-10-01', '2026-10-07');

  expect(trends.days).toEqual([
    '2026-10-01', '2026-10-02', '2026-10-03', '2026-10-04', '2026-10-05', '2026-10-06', '2026-10-07',
  ]);
  expect(trends.series.sleep).toHaveLength(7);
  expect(trends.series.hrv).toHaveLength(7);
  expect(trends.series.restingHr).toHaveLength(7);
});

test('handles ranges that cross a month boundary', () => {
  const trends = buildHealthTrends([], [], '2026-09-29', '2026-10-02');

  expect(trends.days).toEqual(['2026-09-29', '2026-09-30', '2026-10-01', '2026-10-02']);
});

test('maps metrics onto their day and converts sleep minutes to hours', () => {
  const trends = buildHealthTrends(
    [day('2026-10-02', { sleep_total_min: 450, hrv_avg_ms: 42.5, resting_hr_bpm: 61 })],
    [],
    '2026-10-01',
    '2026-10-03',
  );

  expect(trends.series.sleep.map((p) => p.y)).toEqual([null, 7.5, null]);
  expect(trends.series.hrv.map((p) => p.y)).toEqual([null, 42.5, null]);
  expect(trends.series.restingHr.map((p) => p.y)).toEqual([null, 61, null]);
});

test('x values are local-midnight dates matching each day', () => {
  const trends = buildHealthTrends([], [], '2026-10-01', '2026-10-02');

  expect(trends.series.sleep.map((p) => toDayKey(p.x))).toEqual(['2026-10-01', '2026-10-02']);
  expect(trends.series.sleep[0].x.getHours()).toBe(0);
});

test('keeps partial days: a missing metric stays null while others are present', () => {
  const trends = buildHealthTrends(
    [day('2026-10-01', { resting_hr_bpm: 58 })],
    [],
    '2026-10-01',
    '2026-10-01',
  );

  expect(trends.series.restingHr[0].y).toBe(58);
  expect(trends.series.sleep[0].y).toBeNull();
  expect(trends.series.hrv[0].y).toBeNull();
  expect(trends.hasData).toEqual({ sleep: false, hrv: false, restingHr: true });
});

test('ignores health days outside the range', () => {
  const trends = buildHealthTrends(
    [day('2026-09-15', { hrv_avg_ms: 50 })],
    [],
    '2026-10-01',
    '2026-10-02',
  );

  expect(trends.hasData.hrv).toBe(false);
});

test('collapses multiple symptom logs to unique, sorted, in-range days', () => {
  const trends = buildHealthTrends(
    [],
    [
      { timestamp: localIso(2026, 10, 3, 9) },
      { timestamp: localIso(2026, 10, 1, 8) },
      { timestamp: localIso(2026, 10, 3, 20) },
      { timestamp: localIso(2026, 9, 20) }, // before range
      { timestamp: localIso(2026, 10, 9) }, // after range
    ],
    '2026-10-01',
    '2026-10-05',
  );

  expect(trends.symptomDays).toEqual(['2026-10-01', '2026-10-03']);
});

test('buckets late-evening symptom logs on the local calendar day', () => {
  const trends = buildHealthTrends([], [{ timestamp: localIso(2026, 10, 2, 23) }], '2026-10-01', '2026-10-03');

  expect(trends.symptomDays).toEqual(['2026-10-02']);
});

test('reports no data when there are no health days', () => {
  const trends = buildHealthTrends([], [{ timestamp: localIso(2026, 10, 1) }], '2026-10-01', '2026-10-02');

  expect(trends.hasData).toEqual({ sleep: false, hrv: false, restingHr: false });
});

test('parseDayKey and toDayKey round-trip', () => {
  expect(toDayKey(parseDayKey('2026-02-28'))).toBe('2026-02-28');
});

test('summarizeMetric splits averages by symptom vs. other days, skipping gaps', () => {
  const trends = buildHealthTrends(
    [
      day('2026-10-01', { hrv_avg_ms: 40 }),
      day('2026-10-02', { hrv_avg_ms: 30 }),
      day('2026-10-03', { hrv_avg_ms: 50 }),
      day('2026-10-04', { hrv_avg_ms: 61 }),
    ],
    [{ timestamp: localIso(2026, 10, 2) }, { timestamp: localIso(2026, 10, 5) }],
    '2026-10-01',
    '2026-10-05',
  );

  const summary = summarizeMetric(trends.series.hrv, trends.symptomDays);

  expect(summary.symptomDayAvg).toBe(30); // 10-05 has no reading, so only 10-02 counts
  expect(summary.otherDayAvg).toBe(50.3);
});

test('summarizeMetric returns null averages when a group has no readings', () => {
  const trends = buildHealthTrends([day('2026-10-01', { resting_hr_bpm: 60 })], [], '2026-10-01', '2026-10-02');

  expect(summarizeMetric(trends.series.restingHr, trends.symptomDays)).toEqual({
    symptomDayAvg: null,
    otherDayAvg: 60,
  });
});
