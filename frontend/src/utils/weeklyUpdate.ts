// Dates for the weekly update header and progress card. Updates land on Sundays (docs/model-v2-draft.md, Labels).

const DAY_MS = 24 * 60 * 60 * 1000;

function startOfDay(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

function addDays(date: Date, days: number): Date {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate() + days);
}

export interface WeeklyUpdateInfo {
  week: number; // 1 for the first update after the user's first meal
  updateDate: Date; // the most recent Sunday, or today if it's Sunday
  nextUpdateDate: Date; // the Sunday after that
}

/** Which weekly update the user is on, counted in weeks from their first logged meal. */
export function weeklyUpdateInfo(firstMealAt: Date, today: Date = new Date()): WeeklyUpdateInfo {
  const day = startOfDay(today);
  const updateDate = addDays(day, -day.getDay()); // getDay(): Sunday is 0
  const daysSinceFirstMeal = Math.round((updateDate.getTime() - startOfDay(firstMealAt).getTime()) / DAY_MS);
  return {
    week: Math.max(1, Math.floor(daysSinceFirstMeal / 7) + 1),
    updateDate,
    nextUpdateDate: addDays(updateDate, 7),
  };
}

/** "Oct 20" */
export function shortDate(date: Date): string {
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

/** "Sunday, Oct 27" */
export function weekdayDate(date: Date): string {
  return date.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' });
}
