import { apiClient, ApiError } from './client';
import type { WeeklyResultsResponse } from '../types/weeklyResults';

export const resultsService = {
  // get_weekly_results()
  async getWeeklyResults(): Promise<WeeklyResultsResponse> {
    try {
      const { data } = await apiClient.get<WeeklyResultsResponse>('/results/weekly');
      return data;
    } catch (err: any) {
      throw new ApiError(err.response?.data?.detail ?? 'Failed to load your weekly results');
    }
  },
};
