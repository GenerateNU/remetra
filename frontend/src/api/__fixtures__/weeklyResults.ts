// Sample GET /results/weekly responses, one per screen state. Shapes match the backend; slugs and group ids
// come from backend/data/taxonomy/components.yaml.
import type { WeeklyLabel, WeeklyLabelItem, WeeklyResultsResponse } from '../weekly_results_service';

// First meal about two and a half weeks ago, so the sample header reads like a real user's ("Week 3 update")
const FIRST_MEAL_AT = new Date(Date.now() - 17 * 24 * 60 * 60 * 1000).toISOString();

const item = (id: string, display_name: string, label: WeeklyLabel, members: string[] = [id]): WeeklyLabelItem => ({
  id,
  display_name,
  is_group: members.length > 1,
  member_slugs: members,
  label,
});

// A planted onion trigger, with an always-together group among the other labels.
export const withTrigger: WeeklyResultsResponse = {
  likely_trigger: [item('fructans_allium', 'Onion & garlic family', 'likely_trigger')],
  still_learning: [
    item('dairy', 'Dairy (lactose or milk protein)', 'still_learning', ['lactose', 'milk_protein']),
    item('chili', 'Chili peppers', 'still_learning', ['capsaicin', 'nightshades']),
  ],
  looks_fine: [
    item('wheat', 'Wheat, rye & barley (gluten or wheat carbs)', 'looks_fine', ['gluten', 'fructans_grain']),
    item('egg', 'Egg', 'looks_fine'),
  ],
  no_clear_pattern: false,
  groups_checked: 3,
  groups_total: 31,
  first_meal_at: FIRST_MEAL_AT,
};

// Most foods look fine and nothing is close to a trigger.
export const noClearPattern: WeeklyResultsResponse = {
  likely_trigger: [],
  still_learning: [item('chili', 'Chili peppers', 'still_learning', ['capsaicin', 'nightshades'])],
  looks_fine: [
    item('wheat', 'Wheat, rye & barley (gluten or wheat carbs)', 'looks_fine', ['gluten', 'fructans_grain']),
    item('dairy', 'Dairy (lactose or milk protein)', 'looks_fine', ['lactose', 'milk_protein']),
    item('egg', 'Egg', 'looks_fine'),
  ],
  no_clear_pattern: true,
  groups_checked: 3,
  groups_total: 31,
  first_meal_at: FIRST_MEAL_AT,
};

// Foods have been eaten but nothing has enough data for a label yet.
export const allStillLearning: WeeklyResultsResponse = {
  likely_trigger: [],
  still_learning: [
    item('dairy', 'Dairy (lactose or milk protein)', 'still_learning', ['lactose', 'milk_protein']),
    item('fructans_allium', 'Onion & garlic family', 'still_learning'),
  ],
  looks_fine: [],
  no_clear_pattern: false,
  groups_checked: 0,
  groups_total: 31,
  first_meal_at: FIRST_MEAL_AT,
};

// A new user: no stored confidences or no settled meals yet.
export const empty: WeeklyResultsResponse = {
  likely_trigger: [],
  still_learning: [],
  looks_fine: [],
  no_clear_pattern: false,
  groups_checked: 0,
  groups_total: 0,
  first_meal_at: null,
};
