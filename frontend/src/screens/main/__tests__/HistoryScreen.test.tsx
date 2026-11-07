import { ScrollView } from 'react-native';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import { HistoryScreen } from '../HistoryScreen';
import { foodLogService, FoodLogResponse } from '../../../api/food_log_service';
import { symptomLogService } from '../../../api/symptom_log_service';
import { useBankStore } from '../../../store/bankStore';
import { useCalendarStore } from '../../../store/calendarStore';
import { useUIStore } from '../../../store/uiStore';
import { shiftMonth, monthOf } from '../../../utils/calendarGrid';
import { toDayKey } from '../../../utils/dayKey';

jest.mock('../../../api/food_log_service', () => ({
  foodLogService: { getMyFoodLogs: jest.fn(), updateFoodLog: jest.fn() },
}));
jest.mock('../../../api/symptom_log_service', () => ({
  symptomLogService: { getMySymptomLogs: jest.fn(), updateSymptomLog: jest.fn() },
}));
// A stand-in for the calendar endpoints, answering from the log mocks above, so each test only
// has to say which logs exist. The real grouping and status rules are tested in the backend.
jest.mock('../../../api/calendar_service', () => {
  /* eslint-disable @typescript-eslint/no-require-imports -- jest.mock factories can't use imports */
  const { foodLogService: food } = require('../../../api/food_log_service');
  const { symptomLogService: symptom } = require('../../../api/symptom_log_service');
  const { monthRange } = require('../../../utils/calendarGrid');
  const { addDays, toDayKey } = require('../../../utils/dayKey');
  /* eslint-enable @typescript-eslint/no-require-imports */
  const onDay = (day: string) => (log: { timestamp: string }) => toDayKey(new Date(log.timestamp)) === day;
  const allLogs = () => Promise.all([food.getMyFoodLogs(), symptom.getMySymptomLogs()]);

  return {
    calendarService: {
      async getMonth(month: string) {
        const [foodLogs, symptomLogs] = await allLogs();
        const { start, end } = monthRange(month);
        const days = [];
        for (let day = start; day <= end; day = addDays(day, 1)) {
          const f = foodLogs.filter(onDay(day)).length;
          const s = symptomLogs.filter(onDay(day)).length;
          const status = f && s ? 'complete' : f ? 'food_only' : s ? 'symptoms_only' : 'empty';
          days.push({ date: day, food_count: f, symptom_count: s, has_health_data: false, status });
        }
        const streak = foodLogs.length + symptomLogs.length > 0 ? 1 : 0;
        return { month, days, current_streak: streak, longest_streak: streak };
      },
      async getDayLogs(day: string) {
        const [foodLogs, symptomLogs] = await allLogs();
        return { date: day, food_logs: foodLogs.filter(onDay(day)), symptom_logs: symptomLogs.filter(onDay(day)) };
      },
    },
  };
});

const mockFoodLogs = foodLogService.getMyFoodLogs as jest.Mock;
const mockSymptomLogs = symptomLogService.getMySymptomLogs as jest.Mock;

function foodLog(id: string, foodId: string, timestamp = new Date()): FoodLogResponse {
  const iso = timestamp.toISOString();
  return { id, food_id: foodId, quantity: '1 serving(s)', timestamp: iso, notes: null, username: 'u', created_at: iso };
}

const fetchFoods = jest.fn(async () => {});
const fetchSymptoms = jest.fn(async () => {});

beforeEach(() => {
  jest.clearAllMocks();
  useCalendarStore.getState().clearCalendar();
  useUIStore.setState({ showLogModal: false, initialLogType: 'select_type', logVersion: 0 });
  useBankStore.setState({
    foods: [
      { id: 'chicken', name: 'Chicken', ingredients: [] },
      { id: 'rice', name: 'Rice', ingredients: [] },
    ],
    symptoms: [{ id: 'fatigue', name: 'Fatigue', location: 'General', sensation: 'Tired' }],
    scannedFood: null,
    fetchFoods,
    fetchSymptoms,
  });
  mockFoodLogs.mockResolvedValue([foodLog('1', 'chicken')]);
  mockSymptomLogs.mockResolvedValue([]);
});

test('shows a loading spinner, then today’s logs', async () => {
  render(<HistoryScreen />);

  expect(screen.queryByText('Chicken')).toBeNull();
  expect(await screen.findByText('Chicken')).toBeTruthy();
  expect(screen.getByText('Today')).toBeTruthy();
  expect(screen.getByText('1 entry')).toBeTruthy();
});

test('+ Add Log opens the log modal on today by default', async () => {
  render(<HistoryScreen />);
  await screen.findByText('Chicken');

  fireEvent.press(screen.getByText('Add Log'));

  const { showLogModal, initialLogType, initialLogTimestamp } = useUIStore.getState();
  expect(showLogModal).toBe(true);
  expect(initialLogType).toBe('select_type');
  expect(toDayKey(initialLogTimestamp)).toBe(toDayKey(new Date()));
});

test('+ Add Log opens the log modal on the tapped day', async () => {
  render(<HistoryScreen />);
  await screen.findByText('Chicken');

  // The 15th of last month is always in the past
  const lastMonth = shiftMonth(monthOf(toDayKey(new Date())), -1);
  fireEvent.press(screen.getByLabelText('Previous month'));
  const label = new Date(`${lastMonth}-15T12:00:00`).toLocaleDateString('en-US', { month: 'long', day: 'numeric' });
  fireEvent.press(await screen.findByLabelText(new RegExp(`^${label},`)));
  await screen.findByText('Nothing logged on this day.');

  fireEvent.press(screen.getByText('Add Log'));

  expect(toDayKey(useUIStore.getState().initialLogTimestamp)).toBe(`${lastMonth}-15`);
});

test('pull-to-refresh reloads the food and symptom lists and the logs', async () => {
  render(<HistoryScreen />);
  await screen.findByText('Chicken');
  mockFoodLogs.mockResolvedValue([foodLog('1', 'chicken'), foodLog('2', 'rice')]);

  await act(async () => {
    await screen.UNSAFE_getByType(ScrollView).props.refreshControl.props.onRefresh();
  });

  expect(fetchFoods).toHaveBeenCalled();
  expect(fetchSymptoms).toHaveBeenCalled();
  expect(screen.getByText('Rice')).toBeTruthy();
  expect(screen.getByText('2 entries')).toBeTruthy();
});

test('creating a log refreshes the calendar and the day’s list', async () => {
  render(<HistoryScreen />);
  await screen.findByText('Chicken');
  mockFoodLogs.mockResolvedValue([foodLog('1', 'chicken'), foodLog('2', 'rice')]);

  act(() => useUIStore.getState().notifyLogCreated());

  expect(await screen.findByText('Rice')).toBeTruthy();
});

test('a barcode scan opens the food log', async () => {
  render(<HistoryScreen />);
  await screen.findByText('Chicken');

  act(() => useBankStore.setState({ scannedFood: { name: 'Granola', ingredients: ['oats'] } }));

  expect(useUIStore.getState().showLogModal).toBe(true);
  expect(useUIStore.getState().initialLogType).toBe('food');
});

test('shows an error with Retry when loading fails, and Retry recovers', async () => {
  mockFoodLogs.mockRejectedValueOnce(new Error('network down'));
  render(<HistoryScreen />);

  expect(await screen.findByText('Failed to load logs. Pull down to retry.')).toBeTruthy();

  fireEvent.press(screen.getByText('Retry'));

  expect(await screen.findByText('Chicken')).toBeTruthy();
  expect(screen.queryByText('Retry')).toBeNull();
});

test('shows the empty state when the user has never logged anything', async () => {
  mockFoodLogs.mockResolvedValue([]);
  render(<HistoryScreen />);

  expect(await screen.findByText('No logs yet')).toBeTruthy();
});

test('a day with nothing logged offers to log for that day', async () => {
  // Logged before, but not today
  const lastWeek = new Date();
  lastWeek.setDate(lastWeek.getDate() - 7);
  mockFoodLogs.mockResolvedValue([foodLog('1', 'chicken', lastWeek)]);
  render(<HistoryScreen />);

  expect(await screen.findByText('Nothing logged on this day.')).toBeTruthy();
  fireEvent.press(screen.getByText('+ Log for Today'));
  expect(useUIStore.getState().showLogModal).toBe(true);
});

test('paging months selects a day in the new month, and today when coming back', async () => {
  render(<HistoryScreen />);
  await screen.findByText('Chicken');
  const lastMonth = shiftMonth(monthOf(toDayKey(new Date())), -1);
  const firstLabel = new Date(`${lastMonth}-01T12:00:00`).toLocaleDateString([], {
    weekday: 'long', month: 'long', day: 'numeric',
  });

  fireEvent.press(screen.getByLabelText('Previous month'));
  expect(await screen.findByText(firstLabel)).toBeTruthy();

  fireEvent.press(screen.getByLabelText('Next month'));
  expect(await screen.findByText('Today')).toBeTruthy();
  expect(screen.getByText('Chicken')).toBeTruthy();
});

test('saving an edit refetches the calendar and the day', async () => {
  (foodLogService.updateFoodLog as jest.Mock).mockResolvedValue({});
  render(<HistoryScreen />);
  fireEvent.press(await screen.findByText('Chicken'));
  const callsBefore = mockFoodLogs.mock.calls.length;

  fireEvent.press(await screen.findByText('Save Changes'));

  // The stand-in endpoints read the log mocks, so new calls mean the month and day were refetched
  await waitFor(() => expect(mockFoodLogs.mock.calls.length).toBeGreaterThanOrEqual(callsBefore + 2));
});

test('editing a card still saves', async () => {
  (foodLogService.updateFoodLog as jest.Mock).mockResolvedValue({});
  render(<HistoryScreen />);
  fireEvent.press(await screen.findByText('Chicken'));

  fireEvent.press(await screen.findByText('Save Changes'));

  await waitFor(() => expect(foodLogService.updateFoodLog).toHaveBeenCalledWith('1', expect.anything()));
});
