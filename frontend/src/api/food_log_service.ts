import { apiClient, ApiError } from './client';

export interface CreateFoodLogPayload {
  food_id: string; 
  quantity?: string;
  timestamp: string; 
  notes?: string;
  username: string;
}

export interface UpdateFoodLogPayload {
  quantity?: string;
  timestamp?: string;
  notes?: string;
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

export interface MealFollowUpData {
  log_type: "symptom";
  food_log_id: string;
}

export interface MealFollowUpResponse {
  should_schedule: boolean;
  fire_at: string;
  title: string;
  body: string;
  data: MealFollowUpData;
}

// service functions

export const foodLogService = {

  // create_food_log()
  async createFoodLog(payload: CreateFoodLogPayload): Promise<FoodLogResponse> {
    try {
      const { data } = await apiClient.post<FoodLogResponse>('/food-log/', payload);
      return data;
    } catch (err: any) {
      throw new ApiError(err.response?.data?.detail ?? 'Failed to create food log');
    }
  },

  // get_my_food_logs()
  async getMyFoodLogs(): Promise<FoodLogResponse[]> {
    try {
      const { data } = await apiClient.get<FoodLogResponse[]>('/food-log/user/me');
      return data;
    } catch (err: any) {
      throw new ApiError(err.response?.data?.detail ?? 'Failed to fetch food logs');
    }
  },

  // update_food_log()
  async updateFoodLog(foodLogId: string, payload: UpdateFoodLogPayload): Promise<FoodLogResponse> {
    try {
      const { data } = await apiClient.put<FoodLogResponse>(`/food-log/${foodLogId}`, payload);
      return data;
    } catch (err: any) {
      throw new ApiError(err.response?.data?.detail ?? `Failed to update food log ${foodLogId}`);
    }
  },

  // get_food_log()
  async getFoodLogById(foodLogId: string): Promise<FoodLogResponse> {
    try {
      const { data } = await apiClient.get<FoodLogResponse>(`/food-log/${foodLogId}`);
      return data;
    } catch (err: any) {
      throw new ApiError(err.response?.data?.detail ?? `Failed to fetch food log ${foodLogId}`);
    }
  },

  // delete_food_log()
  async deleteFoodLog(foodLogId: string): Promise<FoodLogResponse> {
    try {
      const { data } = await apiClient.delete<FoodLogResponse>(`/food-log/${foodLogId}`);
      return data;
    } catch (err: any) {
      throw new ApiError(err.response?.data?.detail ?? `Failed to delete food log ${foodLogId}`);
    }
  },

  // get_my_meal_follow_up()
  async getMealFollowUp(foodLogId: string): Promise<MealFollowUpResponse> {
    try {
      const { data } = await apiClient.get<MealFollowUpResponse>(`/meal-follow-ups/${foodLogId}`);
      return data;
    } catch (err: any) {
      throw new ApiError(err.response?.data?.detail ?? 'Failed to fetch meal follow-ups');
    }
  },
};