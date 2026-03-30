import { apiClient } from './client';

export interface SuggestedIngredient {
  name: string;
  buckets: string[];
}

export interface SuggestedBucket {
  name: string;
  description?: string;
}

export interface CreateFoodPayload {
  name: string;
  ingredients: string[];
  username?: string;
}

export interface UpdateFoodPayload {
  name?: string;
  ingredients?: string[];
  username?: string;
}

export interface FoodSuggestionPayload {
  name: string;
  ingredients?: string[];
  selected_tag_ids?: string[];
}

export interface FoodResponse {
  id: string; 
  name: string;
  ingredients: string[];
  username: string | null;
  suggested_ingredients: SuggestedIngredient[];
  suggested_buckets: SuggestedBucket[];
}

export interface FoodSuggestionResponse {
  suggested_ingredients: SuggestedIngredient[];
  suggested_buckets: SuggestedBucket[];
}

export class FoodError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'FoodError';
  }
}

// Service functions 

export const foodService = {

  // create_food()
  async createFood(payload: CreateFoodPayload): Promise<FoodResponse> {
    try {
      const { data } = await apiClient.post<FoodResponse>('/food/', payload);
      return data;
    } catch (err: any) {
      throw new FoodError(err.response?.data?.detail ?? 'Failed to create food');
    }
  },

  // suggest_tags()
  async getSuggestions(payload: FoodSuggestionPayload): Promise<FoodSuggestionResponse> {
    try {
      const { data } = await apiClient.post<FoodSuggestionResponse>('/food/suggestions', payload);
      return data;
    } catch (err: any) {
      throw new FoodError(err.response?.data?.detail ?? 'Failed to fetch suggestions');
    }
  },

  // get_all_foods()
  async getAllFoods(): Promise<FoodResponse[]> {
    try {
      const { data } = await apiClient.get<FoodResponse[]>('/food/');
      return data;
    } catch (err: any) {
      throw new FoodError(err.response?.data?.detail ?? 'Failed to fetch foods');
    }
  },

  // get_food()
  async getFoodById(food_id: string): Promise<FoodResponse> {
    try {
      const { data } = await apiClient.get<FoodResponse>(`/food/${food_id}`);
      return data;
    } catch (err: any) {
      throw new FoodError(err.response?.data?.detail ?? `Failed to fetch food ${food_id}`);
    }
  },

  // update_food()
  async updateFood(food_id: string, payload: UpdateFoodPayload): Promise<FoodResponse> {
    try {
      const { data } = await apiClient.put<FoodResponse>(`/food/${food_id}`, payload);
      return data;
    } catch (err: any) {
      throw new FoodError(err.response?.data?.detail ?? `Failed to update food ${food_id}`);
    }
  },

  // delete_food()
  async deleteFood(food_id: string): Promise<FoodResponse> {
    try {
      const { data } = await apiClient.delete<FoodResponse>(`/food/${food_id}`);
      return data;
    } catch (err: any) {
      throw new FoodError(err.response?.data?.detail ?? `Failed to delete food ${food_id}`);
    }
  },
};