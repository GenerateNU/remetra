import { create } from 'zustand';
import { calendarService, CalendarMonthResponse, DayLogsResponse } from '../api/calendar_service';
import { monthOf, shiftMonth } from '../utils/calendarGrid';
import { toDayKey } from '../utils/dayKey';

interface CalendarStore {
  months: Record<string, CalendarMonthResponse>; // keyed by YYYY-MM
  days: Record<string, DayLogsResponse>; // keyed by YYYY-MM-DD
  loadMonth: (month: string) => Promise<void>;
  loadDay: (day: string) => Promise<void>;
  prefetchAround: (month: string) => void;
  refresh: (month: string, day: string) => Promise<void>;
  clearCalendar: () => void;
}

export const useCalendarStore = create<CalendarStore>((set, get) => ({
  months: {},
  days: {},

  // Cached months and days are served as-is; refresh() is what picks up new or edited logs
  loadMonth: async (month) => {
    if (get().months[month]) return;
    const data = await calendarService.getMonth(month);
    set((s) => ({ months: { ...s.months, [month]: data } }));
  },

  loadDay: async (day) => {
    if (get().days[day]) return;
    const data = await calendarService.getDayLogs(day);
    set((s) => ({ days: { ...s.days, [day]: data } }));
  },

  /** Warm the previous and next month so paging is instant. Never goes past the current month. */
  prefetchAround: (month) => {
    const neighbors = [shiftMonth(month, -1), shiftMonth(month, 1)].filter((m) => m <= monthOf(toDayKey(new Date())));
    for (const m of neighbors) get().loadMonth(m).catch(() => {});
  },

  /**
   * Refetch the visible month and day after a log is created or edited. Everything else cached is
   * dropped, since a log can move between days or months. The visible data is only replaced once
   * the new data arrives, so the screen doesn't flash empty.
   */
  refresh: async (month, day) => {
    calendarService.clearCache();
    const [monthData, dayData] = await Promise.all([calendarService.getMonth(month), calendarService.getDayLogs(day)]);
    set({ months: { [month]: monthData }, days: { [day]: dayData } });
    get().prefetchAround(month);
  },

  clearCalendar: () => {
    calendarService.clearCache();
    set({ months: {}, days: {} });
  },
}));
