import { apiClient } from './client';

<<<<<<< HEAD
=======
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

>>>>>>> 15400cce4313ac3e5ae1901f6f5ae555c2cbd432
export interface KeyMetrics {
  exposures: number;
  trigger_rate: number;
  base_rate: number;
  fishers_p_value: number;
  average_intensity: number;
}

<<<<<<< HEAD
export interface AlgorithmAssociation {
=======
export interface AlgorithmAssociationResponse {
>>>>>>> 15400cce4313ac3e5ae1901f6f5ae555c2cbd432
  id: string;
  user_id: string;
  symptom_id: string;
  associated_food_id: string;
<<<<<<< HEAD
=======
  ingredients: string[];
>>>>>>> 15400cce4313ac3e5ae1901f6f5ae555c2cbd432
  key_metrics: KeyMetrics;
  updated_at: string;
}

export interface AlgorithmRunRequest {
  user_id: string;
  symptom_ids?: string[];
  time_window_hours?: number;
}

<<<<<<< HEAD
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
=======
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
  // GET /algorithm/user/{user_id}?symptom_id=...
  async getCorrelations(
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
      throw new AlgorithmError(
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
      throw new AlgorithmError(
        err?.response?.data?.detail ?? 'Failed to run algorithm'
      );
    }
>>>>>>> 15400cce4313ac3e5ae1901f6f5ae555c2cbd432
  },
};
