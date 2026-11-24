/** Mirrors backend/schemas/weekly_results.py (GET /results/weekly). Labels only, never confidence numbers. */

export type WeeklyLabel = 'likely_trigger' | 'still_learning' | 'looks_fine';

export interface WeeklyLabelItem {
  /** Component slug, or merge group id when is_group is true */
  id: string;
  display_name: string;
  /** Always-together foods (e.g. wheat: gluten + wheat fructans) are labelled as one group */
  is_group: boolean;
  member_slugs: string[];
  label: WeeklyLabel;
}

export interface WeeklyResultsResponse {
  likely_trigger: WeeklyLabelItem[];
  still_learning: WeeklyLabelItem[];
  looks_fine: WeeklyLabelItem[];
  /** At least 60% of eaten foods look fine and nothing is close to a trigger */
  no_clear_pattern: boolean;
}
