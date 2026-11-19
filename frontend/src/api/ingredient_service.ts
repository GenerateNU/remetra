import { apiClient, ApiError } from './client';

export interface IngredientLabelsPayload {
  avoid: string[];
  suspect: string[];
  safe: string[];
}

export const ingredientService = {
  // PUT /users/me/ingredients/labels -> replace_my_ingredient_labels()
  async replaceLabels(payload: IngredientLabelsPayload): Promise<void> {
    try {
      await apiClient.put('/users/me/ingredients/labels', payload);
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      const message = typeof detail === 'string' ? detail : 'Failed to save food preferences';
      throw new ApiError(message);
    }
  },
};
