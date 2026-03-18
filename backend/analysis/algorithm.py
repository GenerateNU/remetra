from analysis.models import FoodLogEntry, SymptomLogEntry
from analysis.per_ingredient_counts import count_ingredient_occurrences
from analysis.search import get_food_logs_within_time_window_before_symptom, SymptomFoodWindowResult

from collections import defaultdict

def get_analysis(
  food_logs: list[FoodLogEntry],
  symptom_logs: list[SymptomLogEntry],
  time_window_hours: float,
) -> any:
  total_counts_map: dict[str, int] = count_ingredient_occurrences(food_logs)
  counts: dict[str, dict[str, list]] = get_food_symptom_counts(food_logs, symptom_logs, time_window_hours)
  
def get_food_symptom_counts(
    food_logs: list[FoodLogEntry],
    symptom_logs: list[SymptomLogEntry],
    time_window_hours: float,
) -> dict[str, dict[str, list]]:
  
  # symptom_name -> ingredient -> [count, 
  counts: dict[str, dict[str, list]] = defaultdict(
    lambda: defaultdict(lambda: [0, []])
)

  foods_before_symptom: list[SymptomFoodWindowResult] = get_food_logs_within_time_window_before_symptom(
    food_logs,
    symptom_logs,
    time_window_hours
  )

  # loop through all symptom -> foods pairings and track ingredient counts
  for windowResult in foods_before_symptom:
    symp = windowResult.symptom_log
    s_name = symp.symptom_name

    # union all ingredients across foods in this window
    unique_ingredients: set[str] = set()
    for food in windowResult.food_logs:
        unique_ingredients.update(food.ingredients)

    # now count each ingredient once per symptom event (only for the sake of future metric computation)
    for ingredient in unique_ingredients:
        entry = counts[s_name][ingredient]
        entry[0] += 1
        entry[1].append(symp.intensity)
    
  return counts



