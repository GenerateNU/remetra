import { apiClient } from './client';

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
  // POST /algorithm/run
  async runAlgorithm(payload: AlgorithmRunRequest): Promise<AlgorithmRunResponse> {
    try {
      const { data } = await apiClient.post<AlgorithmRunResponse>('/algorithm/run', payload);
      return data;
    } catch (err: any) {
      throw new AlgorithmError(err?.response?.data?.detail ?? 'Failed to run algorithm');
    }
  },

  // GET /algorithm/user/{user_id}
  async getAssociations(userId: string, symptomId?: string): Promise<AlgorithmAssociationResponse[]> {
    try {
      const { data } = await apiClient.get<AlgorithmAssociationResponse[]>(`/algorithm/user/${userId}`, {
        params: symptomId ? { symptom_id: symptomId } : undefined,
      });
      return data;
    } catch (err: any) {
      throw new AlgorithmError(err?.response?.data?.detail ?? 'Failed to fetch associations');
    }
  },
};
