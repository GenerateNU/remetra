import { apiClient } from './client';

export interface KeyMetrics {
  exposures: number;
  trigger_rate: number;
  base_rate: number;
  fishers_p_value: number;
  average_intensity: number;
}

export interface AlgorithmAssociation {
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

export const algorithmService = {
  // GET /algorithm/user/{user_id}
  async getAssociations(userId: string, symptomId?: string): Promise<AlgorithmAssociation[]> {
    const params = symptomId ? { symptom_id: symptomId } : {};
    const { data } = await apiClient.get(`/algorithm/user/${userId}`, { params });
    return data;
  },

  // POST /algorithm/run
  async runAlgorithm(payload: AlgorithmRunRequest): Promise<AlgorithmAssociation[]> {
    const { data } = await apiClient.post('/algorithm/run', payload);
    return data.associations;
  },
};
