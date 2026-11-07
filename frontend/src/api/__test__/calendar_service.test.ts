import { calendarService, deviceTimeZone } from '../calendar_service';
import { apiClient, ApiError } from '../client';

jest.mock('../client', () => ({
  ...jest.requireActual('../client'),
  apiClient: { get: jest.fn() },
}));

const mockGet = apiClient.get as jest.Mock;

beforeEach(() => jest.clearAllMocks());

test('deviceTimeZone is an IANA name', () => {
  expect(deviceTimeZone()).toEqual(Intl.DateTimeFormat().resolvedOptions().timeZone);
});

test('getMonth asks for the month in the device timezone', async () => {
  const month = { month: '2026-10', days: [], current_streak: 0, longest_streak: 0 };
  mockGet.mockResolvedValue({ data: month });

  await expect(calendarService.getMonth('2026-10')).resolves.toEqual(month);
  expect(mockGet).toHaveBeenCalledWith('/calendar/month', { params: { month: '2026-10', tz: deviceTimeZone() } });
});

test('getDayLogs asks for the day in the device timezone', async () => {
  const day = { date: '2026-10-12', food_logs: [], symptom_logs: [] };
  mockGet.mockResolvedValue({ data: day });

  await expect(calendarService.getDayLogs('2026-10-12')).resolves.toEqual(day);
  expect(mockGet).toHaveBeenCalledWith('/calendar/day', { params: { date: '2026-10-12', tz: deviceTimeZone() } });
});

test('errors carry the backend detail', async () => {
  mockGet.mockRejectedValue({ response: { data: { detail: 'Unknown timezone' } } });

  await expect(calendarService.getMonth('2026-10')).rejects.toEqual(new ApiError('Unknown timezone'));
});
