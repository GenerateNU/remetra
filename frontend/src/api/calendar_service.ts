import { apiClient, ApiError } from './client';
import type { FoodLogResponse } from './food_log_service';
import type { SymptomLogResponse } from './symptom_log_service';

export type DayStatus = 'complete' | 'food_only' | 'symptoms_only' | 'empty';

export interface CalendarDayResponse {
  date: string; // YYYY-MM-DD in the user's local timezone
  food_count: number;
  symptom_count: number;
  has_health_data: boolean;
  status: DayStatus; // decided by the backend; the app only displays it
}

export interface CalendarMonthResponse {
  month: string; // YYYY-MM
  days: CalendarDayResponse[]; // one per day of the month, in order
  current_streak: number; // over the user's whole history, not just this month
  longest_streak: number;
}

export interface DayLogsResponse {
  date: string;
  food_logs: FoodLogResponse[]; // oldest first
  symptom_logs: SymptomLogResponse[];
}

/**
 * The device's IANA timezone. The backend groups logs into days on this clock, which is the same
 * clock the app uses for day keys, so a 23:30 log lands on the same date in the grid and the list.
 */
export function deviceTimeZone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
}

export const calendarService = {

  // get_calendar_month()
  async getMonth(month: string): Promise<CalendarMonthResponse> {
    try {
      const { data } = await apiClient.get<CalendarMonthResponse>('/calendar/month', {
        params: { month, tz: deviceTimeZone() },
      });
      return data;
    } catch (err: any) {
      throw new ApiError(err.response?.data?.detail ?? `Failed to load calendar for ${month}`);
    }
  },

  // get_calendar_day()
  async getDayLogs(day: string): Promise<DayLogsResponse> {
    try {
      const { data } = await apiClient.get<DayLogsResponse>('/calendar/day', {
        params: { date: day, tz: deviceTimeZone() },
      });
      return data;
    } catch (err: any) {
      throw new ApiError(err.response?.data?.detail ?? `Failed to load logs for ${day}`);
    }
  },
};
