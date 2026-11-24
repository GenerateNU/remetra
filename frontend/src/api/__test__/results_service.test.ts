import { resultsService } from '../results_service';
import { apiClient, ApiError } from '../client';

jest.mock('../client', () => ({
  ...jest.requireActual('../client'),
  apiClient: { get: jest.fn() },
}));

const mockGet = apiClient.get as jest.Mock;

beforeEach(() => jest.clearAllMocks());

test('getWeeklyResults calls GET /results/weekly', async () => {
  const results = { likely_trigger: [], still_learning: [], looks_fine: [], no_clear_pattern: false };
  mockGet.mockResolvedValue({ data: results });

  await expect(resultsService.getWeeklyResults()).resolves.toEqual(results);
  expect(mockGet).toHaveBeenCalledWith('/results/weekly');
});

test('errors carry the backend detail', async () => {
  mockGet.mockRejectedValue({ response: { data: { detail: 'Failed to fetch weekly results' } } });

  await expect(resultsService.getWeeklyResults()).rejects.toEqual(new ApiError('Failed to fetch weekly results'));
});

test('errors without a detail get a default message', async () => {
  mockGet.mockRejectedValue(new Error('Network Error'));

  await expect(resultsService.getWeeklyResults()).rejects.toEqual(new ApiError('Failed to load your weekly results'));
});
