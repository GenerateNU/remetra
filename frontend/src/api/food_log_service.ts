import { apiClient } from './client';

export interface CreateFoodLogPayload {
  food_id: string; 
  quantity?: string;
  timestamp: string; 
  notes?: string;
  username: string;
}

export interface FoodLogResponse {
  id: string; 
  food_id: string;
  quantity: string | null;
  timestamp: string;
  notes: string | null;
  username: string;
  created_at: string;
}

export class FoodLogError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'FoodLogError';
  }
}

// service functions

export const foodLogService = {

  // create_food_log()
  async createFoodLog(payload: CreateFoodLogPayload): Promise<FoodLogResponse> {
    try {
      const { data } = await apiClient.post<FoodLogResponse>('/food-log/', payload);
      return data;
    } catch (err: any) {
      throw new FoodLogError(err.response?.data?.detail ?? 'Failed to create food log');
    }
  },

  // get_my_food_logs()
  async getMyFoodLogs(): Promise<FoodLogResponse[]> {
    try {
      const { data } = await apiClient.get<FoodLogResponse[]>('/food-log/user/me');
      return data;
    } catch (err: any) {
      throw new FoodLogError(err.response?.data?.detail ?? 'Failed to fetch food logs');
    }
  },

  // get_food_log()
  async getFoodLogById(foodLogId: string): Promise<FoodLogResponse> {
    try {
      const { data } = await apiClient.get<FoodLogResponse>(`/food-log/${foodLogId}`);
      return data;
    } catch (err: any) {
      throw new FoodLogError(err.response?.data?.detail ?? `Failed to fetch food log ${foodLogId}`);
    }
  },

  // delete_food_log()
  async deleteFoodLog(foodLogId: string): Promise<FoodLogResponse> {
    try {
      const { data } = await apiClient.delete<FoodLogResponse>(`/food-log/${foodLogId}`);
      return data;
    } catch (err: any) {
      throw new FoodLogError(err.response?.data?.detail ?? `Failed to delete food log ${foodLogId}`);
    }
  },
};