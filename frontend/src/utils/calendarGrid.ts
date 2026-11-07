import { addDays, parseDayKey, toDayKey } from './dayKey';

/** An inclusive range of day keys. */
export interface DayRange {
  start: string;
  end: string;
}

export interface CalendarCell<T> {
  date: Date;
  day: string; // day key, YYYY-MM-DD
  inRange: boolean; // false for padding cells before the range starts / after it ends
  data: T | null; // whatever the calendar put in this cell; always null for padding cells
}

export interface CalendarGrid<T> {
  weeks: CalendarCell<T>[][]; // oldest first; each has 7 cells, Monday -> Sunday
  monthLabels: (string | null)[]; // per week: month name where a month starts, else null
}

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const MONTH_KEY = /^(\d{4})-(0[1-9]|1[0-2])$/;

/** 0 = Monday ... 6 = Sunday */
function weekdayIndex(d: Date): number {
  return (d.getDay() + 6) % 7;
}

/** The last `days` days ending on `end`, inclusive. */
export function rollingRange(end: string, days: number): DayRange {
  return { start: addDays(end, -(days - 1)), end };
}

/** The first through last day of a YYYY-MM month. */
export function monthRange(month: string): DayRange {
  const match = MONTH_KEY.exec(month);
  if (!match) throw new Error(`Invalid month: ${month}`);
  const year = Number(match[1]);
  const monthIndex = Number(match[2]) - 1;
  // Day 0 of the next month is the last day of this one
  return { start: `${month}-01`, end: toDayKey(new Date(year, monthIndex + 1, 0)) };
}

/** The YYYY-MM month `n` months after `month` (negative goes back), for prev/next navigation. */
export function shiftMonth(month: string, n: number): string {
  const { start } = monthRange(month);
  const date = parseDayKey(start);
  date.setMonth(date.getMonth() + n);
  return toDayKey(date).slice(0, 7);
}

/** The YYYY-MM month a day key falls in. */
export function monthOf(day: string): string {
  return day.slice(0, 7);
}

/**
 * Lays `range` out as a calendar: one row per week (Monday-first), padded out to whole weeks.
 * The grid knows nothing about what a day means; `cellData` is called for each in-range day and
 * its result is stored on the cell, so each calendar decides what goes in a cell.
 */
export function buildCalendarGrid<T>(
  range: DayRange,
  cellData: (day: string, date: Date) => T | null = () => null,
): CalendarGrid<T> {
  const first = parseDayKey(range.start);
  const last = parseDayKey(range.end);
  if (first > last) throw new Error(`Range starts after it ends: ${range.start} > ${range.end}`);

  // Pad back to the Monday of the first week and forward to the Sunday of the last
  const cursor = new Date(first);
  cursor.setDate(cursor.getDate() - weekdayIndex(first));
  const gridEnd = new Date(last);
  gridEnd.setDate(gridEnd.getDate() + (6 - weekdayIndex(last)));

  const weeks: CalendarCell<T>[][] = [];
  const monthLabels: (string | null)[] = [];
  while (cursor <= gridEnd) {
    const week: CalendarCell<T>[] = [];
    let label: string | null = null;
    for (let i = 0; i < 7; i++) {
      const date = new Date(cursor);
      const day = toDayKey(date);
      const inRange = date >= first && date <= last;
      week.push({ date, day, inRange, data: inRange ? cellData(day, date) : null });
      // Label the first row, and any row where an in-range month starts
      if (inRange && (weeks.length === 0 || date.getDate() === 1) && label === null) {
        label = MONTHS[date.getMonth()];
      }
      cursor.setDate(cursor.getDate() + 1);
    }
    weeks.push(week);
    monthLabels.push(label);
  }

  return { weeks, monthLabels };
}
