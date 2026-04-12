import { apiClient, ApiError } from './client';

export interface CreateSymptomLogPayload {
  symptom_id: string; 
  intensity: number; 
  timestamp: string; 
  duration?: number; 
  notes?: string;
  username: string;
}

export interface UpdateSymptomLogPayload {
  intensity?: number;
  timestamp?: string;
  duration?: number;
  notes?: string;
}

export interface SymptomLogResponse {
  id: string;
  symptom_id: string; 
  intensity: number;
  timestamp: string;
  duration: number | null;
  notes: string | null;
  username: string;
  created_at: string;
}

export const symptomLogService = {

  // create_symptom_log()
  async createSymptomLog(payload: CreateSymptomLogPayload): Promise<SymptomLogResponse> {
    try {
      const { data } = await apiClient.post<SymptomLogResponse>('/symptom-logs/', payload);
      return data;
    } catch (err: any) {
      throw new ApiError(err.response?.data?.detail ?? 'Failed to create symptom log');
    }
  },

  // get_my_symptom_logs()
  async getMySymptomLogs(): Promise<SymptomLogResponse[]> {
    try {
      const { data } = await apiClient.get<SymptomLogResponse[]>('/symptom-logs/user/me');
      return data;
    } catch (err: any) {
      throw new ApiError(err.response?.data?.detail ?? 'Failed to fetch symptom logs');
    }
  },

  // update_symptom_log()
  async updateSymptomLog(logId: string, payload: UpdateSymptomLogPayload): Promise<SymptomLogResponse> {
    try {
      const { data } = await apiClient.put<SymptomLogResponse>(`/symptom-logs/${logId}`, payload);
      return data;
    } catch (err: any) {
      throw new ApiError(err.response?.data?.detail ?? `Failed to update symptom log ${logId}`);
    }
  },

  // get_symptom_log()
  async getSymptomLogById(logId: string): Promise<SymptomLogResponse> {
    try {
      const { data } = await apiClient.get<SymptomLogResponse>(`/symptom-logs/${logId}`);
      return data;
    } catch (err: any) {
      throw new ApiError(err.response?.data?.detail ?? `Failed to fetch symptom log ${logId}`);
    }
  },

  // delete_symptom_log()
  async deleteSymptomLog(logId: string): Promise<void> {
    try {
      await apiClient.delete(`/symptom-logs/${logId}`);
    } catch (err: any) {
      throw new ApiError(err.response?.data?.detail ?? `Failed to delete symptom log ${logId}`);
    }
  },
};