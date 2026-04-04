import { apiClient } from './client';

export interface CreateSymptomPayload {
  name: string;
  location?: string;
  sensation?: string;
  username?: string;
}

export interface UpdateSymptomPayload {
  name?: string;
  location?: string;
  sensation?: string;
  username?: string;
}

export interface SymptomResponse {
  id: string; 
  name: string;
  location: string | null;
  sensation: string | null;
  username: string | null;
  created_at: string;
}

export class SymptomError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'SymptomError';
  }
}

export const symptomService = {

  // create_symptom()
  async createSymptom(payload: CreateSymptomPayload): Promise<SymptomResponse> {
    try {
      const { data } = await apiClient.post<SymptomResponse>('/symptom/', payload);
      return data;
    } catch (err: any) {
      throw new SymptomError(err.response?.data?.detail ?? 'Failed to create symptom');
    }
  },

  // get_all_symptoms()
  async getAllSymptoms(): Promise<SymptomResponse[]> {
    try {
      const { data } = await apiClient.get<SymptomResponse[]>('/symptom/');
      return data;
    } catch (err: any) {
      throw new SymptomError(err.response?.data?.detail ?? 'Failed to fetch symptoms');
    }
  },

  // get_symptom()
  async getSymptomById(symptomId: string): Promise<SymptomResponse> {
    try {
      const { data } = await apiClient.get<SymptomResponse>(`/symptom/${symptomId}`);
      return data;
    } catch (err: any) {
      throw new SymptomError(err.response?.data?.detail ?? `Failed to fetch symptom ${symptomId}`);
    }
  },

  // update_symptom()
  async updateSymptom(symptomId: string, payload: UpdateSymptomPayload): Promise<SymptomResponse> {
    try {
      const { data } = await apiClient.put<SymptomResponse>(`/symptom/${symptomId}`, payload);
      return data;
    } catch (err: any) {
      throw new SymptomError(err.response?.data?.detail ?? `Failed to update symptom ${symptomId}`);
    }
  },

  // delete_symptom()
  async deleteSymptom(symptomId: string): Promise<SymptomResponse> {
    try {
      const { data } = await apiClient.delete<SymptomResponse>(`/symptom/${symptomId}`);
      return data;
    } catch (err: any) {
      throw new SymptomError(err.response?.data?.detail ?? `Failed to delete symptom ${symptomId}`);
    }
  },
};