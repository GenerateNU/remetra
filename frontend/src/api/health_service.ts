import { apiClient, ApiError } from './client';

export interface HealthDayResponse {
  date: string; // YYYY-MM-DD, in the timezone the user's health data was synced in
  sleep_total_min: number | null;
  hrv_avg_ms: number | null;
  resting_hr_bpm: number | null;
  symptom_count: number;
  max_intensity: number | null;
}

export const healthService = {

  // get_health_trends() — one entry per day in [start, end]; range capped at 90 days by the backend
  async getHealthTrends(start: string, end: string): Promise<HealthDayResponse[]> {
    try {
      const { data } = await apiClient.get<HealthDayResponse[]>('/health/trends', {
        params: { start, end },
      });
      return data;
    } catch (err: any) {
      throw new ApiError(err.response?.data?.detail ?? 'Failed to fetch health trends');
    }
  },
};
