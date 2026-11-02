import { ApiError } from './client';
import { foodLogService, FoodLogResponse } from './food_log_service';
import { symptomLogService, SymptomLogResponse } from './symptom_log_service';
import { monthRange } from '../utils/calendarGrid';
import { addDays, toDayKey } from '../utils/dayKey';

export type DayStatus = 'complete' | 'food_only' | 'symptoms_only' | 'empty';

export interface CalendarDayResponse {
  date: string; // YYYY-MM-DD in the user's local timezone
  food_count: number;
  symptom_count: number;
  has_health_data: boolean;
  status: DayStatus;
}

export interface CalendarMonthResponse {
  month: string; // YYYY-MM
  days: CalendarDayResponse[]; // one per day of the month, in order
  current_streak: number; // over the user's whole history, not just this month
  longest_streak: number;
}

export interface DayLogsResponse {
  date: string;
  food_logs: FoodLogResponse[];
  symptom_logs: SymptomLogResponse[];
}

// ─── temporary on-device implementation ──────────────────────────────────────
// The calendar endpoints aren't built yet, so the responses above are derived here from the
// user's full log history, grouped by the device's local day. Once the backend serves them,
// replace the calendarService bodies with apiClient calls and delete this section; the backend
// then owns the status and streak rules.

type AllLogs = { food: FoodLogResponse[]; symptom: SymptomLogResponse[] };
let allLogs: Promise<AllLogs> | null = null;

function loadAllLogs(): Promise<AllLogs> {
  if (!allLogs) {
    allLogs = Promise.all([foodLogService.getMyFoodLogs(), symptomLogService.getMySymptomLogs()]).then(
      ([food, symptom]) => ({ food, symptom }),
    );
    // Don't cache a failure, so the next call retries
    allLogs.catch(() => {
      allLogs = null;
    });
  }
  return allLogs;
}

export function dayStatus(foodCount: number, symptomCount: number): DayStatus {
  if (foodCount > 0 && symptomCount > 0) return 'complete';
  if (foodCount > 0) return 'food_only';
  if (symptomCount > 0) return 'symptoms_only';
  return 'empty';
}

function countByDay(logs: { timestamp: string }[]): Map<string, number> {
  const counts = new Map<string, number>();
  for (const log of logs) {
    const day = toDayKey(new Date(log.timestamp));
    counts.set(day, (counts.get(day) ?? 0) + 1);
  }
  return counts;
}

/**
 * Streaks over every day with at least one log. The current streak counts back from today, or
 * from yesterday if today has nothing yet, so it doesn't reset before the user has had a chance
 * to log.
 */
export function computeStreaks(loggedDays: Set<string>, today: string): { current: number; longest: number } {
  let current = 0;
  let cursor = loggedDays.has(today) ? today : addDays(today, -1);
  while (loggedDays.has(cursor)) {
    current += 1;
    cursor = addDays(cursor, -1);
  }

  let longest = 0;
  let run = 0;
  let prev: string | null = null;
  for (const day of [...loggedDays].sort()) {
    run = prev !== null && addDays(prev, 1) === day ? run + 1 : 1;
    longest = Math.max(longest, run);
    prev = day;
  }

  return { current, longest };
}

export function summarizeMonth(month: string, logs: AllLogs, today: string): CalendarMonthResponse {
  const foodCounts = countByDay(logs.food);
  const symptomCounts = countByDay(logs.symptom);
  const { start, end } = monthRange(month);

  const days: CalendarDayResponse[] = [];
  for (let day = start; day <= end; day = addDays(day, 1)) {
    const food = foodCounts.get(day) ?? 0;
    const symptom = symptomCounts.get(day) ?? 0;
    days.push({ date: day, food_count: food, symptom_count: symptom, has_health_data: false, status: dayStatus(food, symptom) });
  }

  const { current, longest } = computeStreaks(new Set([...foodCounts.keys(), ...symptomCounts.keys()]), today);
  return { month, days, current_streak: current, longest_streak: longest };
}

export function logsForDay(day: string, logs: AllLogs): DayLogsResponse {
  const onDay = (log: { timestamp: string }) => toDayKey(new Date(log.timestamp)) === day;
  return { date: day, food_logs: logs.food.filter(onDay), symptom_logs: logs.symptom.filter(onDay) };
}

// ─── service ──────────────────────────────────────────────────────────────────

export const calendarService = {
  async getMonth(month: string): Promise<CalendarMonthResponse> {
    try {
      return summarizeMonth(month, await loadAllLogs(), toDayKey(new Date()));
    } catch (err: any) {
      throw new ApiError(err.message ?? `Failed to load calendar for ${month}`);
    }
  },

  async getDayLogs(day: string): Promise<DayLogsResponse> {
    try {
      return logsForDay(day, await loadAllLogs());
    } catch (err: any) {
      throw new ApiError(err.message ?? `Failed to load logs for ${day}`);
    }
  },

  /** Drop anything cached on the device so the next call sees new or edited logs. */
  clearCache() {
    allLogs = null;
  },
};
