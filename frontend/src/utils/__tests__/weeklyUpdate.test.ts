import { shortDate, weekdayDate, weeklyUpdateInfo } from '../weeklyUpdate';

// Local dates (month is 0-based): Oct 20 2024 is a Sunday, matching the Figma mockup
const date = (month: number, day: number, hour = 12) => new Date(2024, month - 1, day, hour);

describe('weeklyUpdateInfo', () => {
  it('matches the mockup: first meal two weeks before Sunday Oct 20 is week 3', () => {
    const info = weeklyUpdateInfo(date(10, 6, 8), date(10, 23));

    expect(info.week).toBe(3);
    expect(shortDate(info.updateDate)).toBe('Oct 20');
    expect(weekdayDate(info.nextUpdateDate)).toBe('Sunday, Oct 27');
  });

  it('uses today as the update date on a Sunday', () => {
    const info = weeklyUpdateInfo(date(10, 6), date(10, 20, 23));

    expect(shortDate(info.updateDate)).toBe('Oct 20');
    expect(info.week).toBe(3);
  });

  it('counts a first meal mid-week toward that week', () => {
    // First meal Wednesday Oct 9; the next Sunday (Oct 13) is week 1, Oct 20 is week 2
    expect(weeklyUpdateInfo(date(10, 9), date(10, 14)).week).toBe(1);
    expect(weeklyUpdateInfo(date(10, 9), date(10, 21)).week).toBe(2);
  });

  it('never goes below week 1 when the first meal is after the last Sunday', () => {
    expect(weeklyUpdateInfo(date(10, 22), date(10, 23)).week).toBe(1);
  });
});
