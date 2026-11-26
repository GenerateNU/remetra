import { weeklyResultsService } from '../weekly_results_service';
import { apiClient, ApiError } from '../client';
import { withTrigger } from '../__fixtures__/weeklyResults';

jest.mock('../client', () => ({
  ...jest.requireActual('../client'),
  apiClient: { get: jest.fn() },
}));

const mockGet = apiClient.get as jest.Mock;

beforeEach(() => jest.clearAllMocks());

test('getWeekly fetches the signed-in user\'s labels', async () => {
  // Arrange
  mockGet.mockResolvedValue({ data: withTrigger });

  // Act / Assert
  await expect(weeklyResultsService.getWeekly()).resolves.toEqual(withTrigger);
  expect(mockGet).toHaveBeenCalledWith('/results/weekly');
});

test('errors carry the backend detail', async () => {
  mockGet.mockRejectedValue({ response: { data: { detail: 'Failed to fetch weekly results' } } });

  await expect(weeklyResultsService.getWeekly()).rejects.toEqual(new ApiError('Failed to fetch weekly results'));
});

test('errors without a detail fall back to a generic message', async () => {
  mockGet.mockRejectedValue(new Error('Network Error'));

  await expect(weeklyResultsService.getWeekly()).rejects.toEqual(new ApiError('Failed to fetch weekly results'));
});
