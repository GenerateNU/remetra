/**
 * Day keys are local-calendar YYYY-MM-DD strings. Everything that groups by day (calendar grids,
 * the day's log list, API date params) should go through these so a 23:30 log lands on the same
 * day everywhere.
 */

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

/** The day key `n` days after `day` (negative goes back). */
export function addDays(day: string, n: number): string {
  const date = parseDayKey(day);
  date.setDate(date.getDate() + n);
  return toDayKey(date);
}
