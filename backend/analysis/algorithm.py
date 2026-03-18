from analysis.models import FoodLogEntry, SymptomLogEntry, IngredientSymptomMetrics
from analysis.per_ingredient_counts import count_ingredient_occurrences
from analysis.search import get_food_logs_within_time_window_before_symptoms, SymptomFoodWindowResult

from collections import defaultdict
from scipy.stats import fisher_exact


def get_analysis(
    food_logs: list[FoodLogEntry],
    symptom_logs: list[SymptomLogEntry],
    time_window_hours: float,
) -> dict[str, dict[str, IngredientSymptomMetrics]]:
    ingredient_counts, total_food_events = count_ingredient_occurrences(food_logs)
    counts = get_food_symptom_counts(food_logs, symptom_logs, time_window_hours)

    symptom_event_counts: dict[str, int] = defaultdict(int)
    for s in symptom_logs:
        symptom_event_counts[s.symptom_name] += 1

    result: dict[str, dict[str, IngredientSymptomMetrics]] = {}
    for symptom_name, ingredient_data in counts.items():
        result[symptom_name] = {}
        total_symptom_events = symptom_event_counts[symptom_name]

        for ingredient, (co_count, intensities) in ingredient_data.items():
            ingredient_total = ingredient_counts.get(ingredient, 0)

            trigger_rate = co_count / total_symptom_events if total_symptom_events > 0 else 0.0
            base_rate = ingredient_total / total_food_events if total_food_events > 0 else 0.0
            relative_risk = trigger_rate / base_rate if base_rate > 0 else 0.0

            a = co_count
            b = total_symptom_events - co_count
            c = ingredient_total - co_count
            d = total_food_events - ingredient_total - b
            _, p_value = fisher_exact([[a, b], [c, d]], alternative="greater")

            avg_intensity = sum(intensities) / len(intensities) if intensities else 0.0

            result[symptom_name][ingredient] = IngredientSymptomMetrics(
                trigger_rate=trigger_rate,
                base_rate=base_rate,
                relative_risk=relative_risk,
                fishers_p_value=p_value,
                average_intensity=avg_intensity,
            )

    return result


def get_food_symptom_counts(
    food_logs: list[FoodLogEntry],
    symptom_logs: list[SymptomLogEntry],
    time_window_hours: float,
) -> dict[str, dict[str, list]]:
  
  # symptom_name -> ingredient -> [count, 
  counts: dict[str, dict[str, list]] = defaultdict(
    lambda: defaultdict(lambda: [0, []])
)

  foods_before_symptom: list[SymptomFoodWindowResult] = get_food_logs_within_time_window_before_symptoms(
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



