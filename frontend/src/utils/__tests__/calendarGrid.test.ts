import { buildCalendarGrid, monthOf, monthRange, rollingRange, shiftMonth, type CalendarGrid } from '../calendarGrid';
import { addDays, parseDayKey, toDayKey } from '../dayKey';

type Grid = CalendarGrid<unknown>;
const flat = (g: Grid) => g.weeks.flat();
const inRangeDays = (g: Grid) => flat(g).filter((c) => c.inRange).map((c) => c.day);

describe('dayKey', () => {
  test('parseDayKey gives local midnight and round-trips with toDayKey', () => {
    const d = parseDayKey('2026-03-08'); // US DST change day
    expect(d.getHours()).toBe(0);
    expect(toDayKey(d)).toBe('2026-03-08');
  });

  test('toDayKey uses the local day, so a late-evening time stays on that day', () => {
    expect(toDayKey(new Date(2026, 9, 12, 23, 30))).toBe('2026-10-12');
  });

  test('addDays crosses month, year and DST boundaries', () => {
    expect(addDays('2026-10-31', 1)).toBe('2026-11-01');
    expect(addDays('2027-01-01', -1)).toBe('2026-12-31');
    expect(addDays('2026-03-07', 2)).toBe('2026-03-09');
  });
});

describe('ranges', () => {
  test('rollingRange crosses month boundaries and includes both ends', () => {
    expect(rollingRange('2026-10-03', 7)).toEqual({ start: '2026-09-27', end: '2026-10-03' });
    expect(rollingRange('2026-10-03', 1)).toEqual({ start: '2026-10-03', end: '2026-10-03' });
  });

  test('monthRange covers the whole month, including leap Februaries', () => {
    expect(monthRange('2026-10')).toEqual({ start: '2026-10-01', end: '2026-10-31' });
    expect(monthRange('2026-11')).toEqual({ start: '2026-11-01', end: '2026-11-30' });
    expect(monthRange('2027-02')).toEqual({ start: '2027-02-01', end: '2027-02-28' });
    expect(monthRange('2028-02')).toEqual({ start: '2028-02-01', end: '2028-02-29' });
  });

  test('monthRange rejects malformed months', () => {
    expect(() => monthRange('2026-13')).toThrow('Invalid month');
    expect(() => monthRange('2026-1')).toThrow('Invalid month');
    expect(() => monthRange('2026-10-01')).toThrow('Invalid month');
  });

  test('shiftMonth moves across year boundaries', () => {
    expect(shiftMonth('2026-12', 1)).toBe('2027-01');
    expect(shiftMonth('2026-01', -1)).toBe('2025-12');
    expect(shiftMonth('2026-10', 0)).toBe('2026-10');
  });

  test('monthOf gives the month a day falls in', () => {
    expect(monthOf('2026-10-12')).toBe('2026-10');
  });
});

describe('buildCalendarGrid: rolling range', () => {
  // 2026-10-07 is a Wednesday
  test('lays days out in Monday-first weeks of 7', () => {
    const grid = buildCalendarGrid(rollingRange('2026-10-07', 7)); // Thu 10-01 .. Wed 10-07

    expect(grid.weeks).toHaveLength(2);
    expect(grid.weeks.every((w) => w.length === 7)).toBe(true);
    expect(grid.weeks[0][0].day).toBe('2026-09-28'); // Monday
    expect(grid.weeks[1][6].day).toBe('2026-10-11'); // Sunday
  });

  test('90 days fit in 13-14 weeks, ending on the last day', () => {
    const grid = buildCalendarGrid(rollingRange('2026-10-07', 90));

    expect(grid.weeks.length).toBeGreaterThanOrEqual(13);
    expect(grid.weeks.length).toBeLessThanOrEqual(14);
    const days = inRangeDays(grid);
    expect(days).toHaveLength(90);
    expect(days[0]).toBe('2026-07-10');
    expect(days[days.length - 1]).toBe('2026-10-07');
  });

  test('labels the first week and each week where a month starts', () => {
    const grid = buildCalendarGrid(rollingRange('2026-10-07', 30)); // 09-08 .. 10-07

    expect(grid.monthLabels[0]).toBe('Sep');
    expect(grid.monthLabels.filter(Boolean)).toEqual(['Sep', 'Oct']);
  });
});

describe('buildCalendarGrid: calendar month', () => {
  test('pads a month out to whole Monday-first weeks', () => {
    const grid = buildCalendarGrid(monthRange('2026-10')); // Thu 10-01 .. Sat 10-31

    expect(grid.weeks).toHaveLength(5);
    expect(grid.weeks[0][0]).toMatchObject({ day: '2026-09-28', inRange: false });
    expect(grid.weeks[0][3]).toMatchObject({ day: '2026-10-01', inRange: true });
    expect(grid.weeks[4][6]).toMatchObject({ day: '2026-11-01', inRange: false });
    expect(inRangeDays(grid)).toHaveLength(31);
  });

  test('a month starting on Sunday spans 6 weeks', () => {
    const grid = buildCalendarGrid(monthRange('2026-11')); // Sun 11-01 .. Mon 11-30

    expect(grid.weeks).toHaveLength(6);
    expect(grid.weeks[0][6].day).toBe('2026-11-01');
    expect(grid.weeks[5][0].day).toBe('2026-11-30');
  });

  test('a month that starts on Monday and ends on Sunday has no padding', () => {
    const grid = buildCalendarGrid(monthRange('2027-02'));

    expect(grid.weeks).toHaveLength(4);
    expect(flat(grid).every((c) => c.inRange)).toBe(true);
  });

  test('every day appears exactly once across a DST change', () => {
    const days = inRangeDays(buildCalendarGrid(monthRange('2026-03')));

    expect(days).toHaveLength(31);
    expect(new Set(days).size).toBe(31);
    expect(days).toContain('2026-03-08');
  });

  test('only the first week gets a month label', () => {
    const grid = buildCalendarGrid(monthRange('2026-10'));

    expect(grid.monthLabels).toEqual(['Oct', null, null, null, null]);
  });
});

describe('buildCalendarGrid: cell data', () => {
  test('cell data comes from the caller and is only requested for in-range days', () => {
    const requested: string[] = [];
    const grid = buildCalendarGrid(monthRange('2026-10'), (day) => {
      requested.push(day);
      return day === '2026-10-12' ? { status: 'complete' } : null;
    });

    expect(requested).toHaveLength(31);
    expect(requested[0]).toBe('2026-10-01');
    const cells = flat(grid);
    expect(cells.find((c) => c.day === '2026-10-12')!.data).toEqual({ status: 'complete' });
    expect(cells.find((c) => c.day === '2026-10-13')!.data).toBeNull();
    expect(cells.find((c) => c.day === '2026-09-28')!.data).toBeNull(); // padding
  });

  test('without a cellData function every cell is empty', () => {
    expect(flat(buildCalendarGrid(rollingRange('2026-10-07', 7))).every((c) => c.data === null)).toBe(true);
  });

  test('cell dates match their day keys', () => {
    const cells = flat(buildCalendarGrid(monthRange('2026-10')));

    expect(cells.every((c) => toDayKey(c.date) === c.day)).toBe(true);
  });

  test('rejects a range that starts after it ends', () => {
    expect(() => buildCalendarGrid({ start: '2026-10-08', end: '2026-10-07' })).toThrow('starts after');
  });
});
