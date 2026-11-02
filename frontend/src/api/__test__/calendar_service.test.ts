import { computeStreaks, dayStatus, logsForDay, summarizeMonth } from '../calendar_service';
import type { FoodLogResponse } from '../food_log_service';
import type { SymptomLogResponse } from '../symptom_log_service';

// Local times, so the tests group by the same day in any timezone
const at = (y: number, m: number, d: number, h = 12, min = 0) => new Date(y, m - 1, d, h, min).toISOString();

function food(timestamp: string): FoodLogResponse {
  return { id: timestamp, food_id: 'f', quantity: null, timestamp, notes: null, username: 'u', created_at: timestamp };
}

function symptom(timestamp: string): SymptomLogResponse {
  return { id: timestamp, symptom_id: 's', intensity: 3, timestamp, duration: null, notes: null, username: 'u', created_at: timestamp };
}

describe('dayStatus', () => {
  test('needs both food and a symptom to be complete', () => {
    expect(dayStatus(2, 1)).toBe('complete');
    expect(dayStatus(1, 0)).toBe('food_only');
    expect(dayStatus(0, 3)).toBe('symptoms_only');
    expect(dayStatus(0, 0)).toBe('empty');
  });
});

describe('computeStreaks', () => {
  test('current streak counts back from today', () => {
    const days = new Set(['2026-10-10', '2026-10-11', '2026-10-12']);
    expect(computeStreaks(days, '2026-10-12').current).toBe(3);
  });

  test('current streak starts from yesterday when today is not logged yet', () => {
    const days = new Set(['2026-10-10', '2026-10-11']);
    expect(computeStreaks(days, '2026-10-12').current).toBe(2);
  });

  test('a gap before yesterday breaks the current streak', () => {
    expect(computeStreaks(new Set(['2026-10-09']), '2026-10-12').current).toBe(0);
  });

  test('streaks run across month and year boundaries', () => {
    const days = new Set(['2026-12-30', '2026-12-31', '2027-01-01']);
    expect(computeStreaks(days, '2027-01-01')).toEqual({ current: 3, longest: 3 });
  });

  test('longest streak is all-time, not just the current run', () => {
    const days = new Set(['2026-08-01', '2026-08-02', '2026-08-03', '2026-08-04', '2026-10-11', '2026-10-12']);
    expect(computeStreaks(days, '2026-10-12')).toEqual({ current: 2, longest: 4 });
  });

  test('no logs means no streaks', () => {
    expect(computeStreaks(new Set(), '2026-10-12')).toEqual({ current: 0, longest: 0 });
  });
});

describe('summarizeMonth', () => {
  test('returns one entry per day with counts and status', () => {
    const summary = summarizeMonth(
      '2026-10',
      { food: [food(at(2026, 10, 12, 8)), food(at(2026, 10, 12, 19)), food(at(2026, 10, 13))], symptom: [symptom(at(2026, 10, 12))] },
      '2026-10-31',
    );

    expect(summary.days).toHaveLength(31);
    expect(summary.days[11]).toMatchObject({ date: '2026-10-12', food_count: 2, symptom_count: 1, status: 'complete' });
    expect(summary.days[12]).toMatchObject({ date: '2026-10-13', status: 'food_only' });
    expect(summary.days[0]).toMatchObject({ date: '2026-10-01', status: 'empty' });
  });

  test('a 23:30 log counts on that day, not the next', () => {
    const summary = summarizeMonth('2026-10', { food: [food(at(2026, 10, 12, 23, 30))], symptom: [] }, '2026-10-31');

    expect(summary.days[11].food_count).toBe(1);
    expect(summary.days[12].food_count).toBe(0);
  });

  test('streaks include days outside the requested month', () => {
    const logs = { food: [food(at(2026, 9, 30)), food(at(2026, 10, 1))], symptom: [] };
    expect(summarizeMonth('2026-10', logs, '2026-10-01').current_streak).toBe(2);
  });
});

describe('logsForDay', () => {
  test('only returns that local day', () => {
    const logs = { food: [food(at(2026, 10, 12, 23, 30)), food(at(2026, 10, 13, 0, 15))], symptom: [symptom(at(2026, 10, 12))] };
    const day = logsForDay('2026-10-12', logs);

    expect(day.food_logs).toHaveLength(1);
    expect(day.symptom_logs).toHaveLength(1);
  });
});
