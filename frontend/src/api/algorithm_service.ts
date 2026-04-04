import { apiClient } from './client';

export interface CorrelationsRequestParams {
  days: number;
  symptom_ids: number[];
}

export interface CorrelationResult {
  symptom_id: number;
  correlation: number;
}

export type CorrelationsResponse = CorrelationResult[];

export interface AnalyzeRequestPayload {
  days: number;
  symptom_ids: number[];
}

export interface AnalyzeResponse {
  job_id?: string;
  status: 'started' | 'in_progress' | 'completed' | 'failed';
  message?: string;
export interface KeyMetrics {
  exposures: number;
  trigger_rate: number;
  base_rate: number;
  fishers_p_value: number;
  average_intensity: number;
}

export interface AlgorithmAssociationResponse {
  id: string;
  user_id: string;
  symptom_id: string;
  associated_food_id: string;
  key_metrics: KeyMetrics;
  updated_at: string;
}

export interface AlgorithmRunRequest {
  user_id: string;
  symptom_ids?: string[];
  time_window_hours?: number;
}

export interface AlgorithmRunResponse {
  associations: AlgorithmAssociationResponse[];
}

export class AlgorithmError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AlgorithmError';
  }
}

export const algorithmService = {
  // GET /algorithm/correlations
  async getCorrelations(
    params: CorrelationsRequestParams
  ): Promise<CorrelationsResponse> {
    try {
      const { data } = await apiClient.get<CorrelationsResponse>('/algorithm/correlations', {
        params,
      });
      return data;
    } catch (err: any) {
      throw new AlgorithmError(
        err?.response?.data?.detail ?? 'Failed to fetch correlations'
      );
    }
  },

  // POST /algorithm/analyze
  async analyze(
    payload: AnalyzeRequestPayload
  ): Promise<AnalyzeResponse> {
    try {
      const { data } = await apiClient.post<AnalyzeResponse>('/algorithm/analyze', payload);
      return data;
    } catch (err: any) {
      throw new AlgorithmError(
        err?.response?.data?.detail ?? 'Failed to trigger algorithm analysis'
      );
    }
  },
};
