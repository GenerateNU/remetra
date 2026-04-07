import { apiClient, ApiError } from './client';

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
}

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
  ingredients: string[];
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

export const algorithmService = {
  // GET /algorithm/user/{user_id}?symptom_id=...
  async getAssociations(
    userId: string,
    symptomId?: string
  ): Promise<AlgorithmAssociationResponse[]> {
    try {
      const { data } = await apiClient.get<AlgorithmAssociationResponse[]>(
        `/algorithm/user/${userId}`,
        { params: symptomId ? { symptom_id: symptomId } : undefined }
      );
      return data;
    } catch (err: any) {
      throw new ApiError(
        err?.response?.data?.detail ?? 'Failed to fetch correlations'
      );
    }
  },

  // POST /algorithm/run
  async analyze(payload: AlgorithmRunRequest): Promise<AlgorithmRunResponse> {
    try {
      const { data } = await apiClient.post<AlgorithmRunResponse>('/algorithm/run', payload);
      return data;
    } catch (err: any) {
      throw new ApiError(
        err?.response?.data?.detail ?? 'Failed to run algorithm'
      );
    }
  },
};
