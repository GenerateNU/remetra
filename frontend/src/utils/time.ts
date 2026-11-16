/** "1:00 PM" */
export function formatClockTime(value: string | Date): string {
  return new Date(value).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
}

/** "Sunday, Oct 20 · 9:00 AM" */
export function formatDayLabel(value: Date): string {
  const day = value.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' });
  return `${day} · ${formatClockTime(value)}`;
}
