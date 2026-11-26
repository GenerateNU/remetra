import { apiClient, ApiError } from './client';

// Mirrors backend/schemas/weekly_results.py. Labels only: the backend never sends confidence numbers.
export type WeeklyLabel = 'looks_fine' | 'likely_trigger' | 'still_learning';

export interface WeeklyLabelItem {
  id: string; // component slug, or merge group id when is_group is true
  display_name: string;
  is_group: boolean; // always-together foods (e.g. dairy) are labelled as one group
  member_slugs: string[]; // component slugs in the group, or just this component
  label: WeeklyLabel;
}

export interface WeeklyResultsResponse {
  likely_trigger: WeeklyLabelItem[];
  still_learning: WeeklyLabelItem[];
  looks_fine: WeeklyLabelItem[];
  no_clear_pattern: boolean; // at least 60% look fine and nothing is close to a trigger
  groups_checked: number; // food groups with a result (likely trigger or looks fine); a count, not a confidence
  groups_total: number; // every food group the model tracks, merge groups counted once
  first_meal_at: string | null; // ISO timestamp of the user's first meal
}

export const weeklyResultsService = {
  // get_weekly_results() — the signed-in user's food labels
  async getWeekly(): Promise<WeeklyResultsResponse> {
    try {
      const { data } = await apiClient.get<WeeklyResultsResponse>('/results/weekly');
      return data;
    } catch (err: any) {
      throw new ApiError(err.response?.data?.detail ?? 'Failed to fetch weekly results');
    }
  },
};
