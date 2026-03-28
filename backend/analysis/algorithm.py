from collections import defaultdict

from scipy.stats import fisher_exact

from analysis.models import FoodLogEntry, IngredientSymptomMetrics, SymptomLogEntry
from analysis.per_ingredient_counts import count_ingredient_occurrences
from analysis.search import SymptomFoodWindowResult, get_food_logs_within_time_window_before_symptoms


def get_analysis(
    food_logs: list[FoodLogEntry],
    symptom_logs: list[SymptomLogEntry],
    time_window_hours: float,
) -> dict[str, dict[str, IngredientSymptomMetrics]]:
    ingredient_counts, total_food_events = count_ingredient_occurrences(food_logs)
    counts, foods_in_windows = get_food_symptom_counts(food_logs, symptom_logs, time_window_hours)

    result: dict[str, dict[str, IngredientSymptomMetrics]] = {}
    for symptom_name, ingredient_data in counts.items():
        result[symptom_name] = {}
        total_in_window = foods_in_windows[symptom_name]

        for ingredient, (a, intensities) in ingredient_data.items():
            ingredient_total = ingredient_counts.get(ingredient, 0)
            if ingredient_total == 0:
                continue

            # a = food events with ingredient found in symptom windows
            # b = food events with ingredient NOT in any symptom window
            # c = food events WITHOUT ingredient found in symptom windows
            # d = food events WITHOUT ingredient NOT in any symptom window

            b = ingredient_total - a
            c = total_in_window - a
            d = (total_food_events - ingredient_total) - c

            # ── metrics ──
            # trigger_rate: "when you eat X, how often does symptom follow?"
            trigger_rate = a / ingredient_total

            # base_rate: "when you DON'T eat X, how often does symptom follow?"
            unexposed_total = total_food_events - ingredient_total
            base_rate = c / unexposed_total if unexposed_total > 0 else 0.0

            _, p_value = fisher_exact([[a, b], [c, d]], alternative="greater")

            avg_intensity = sum(intensities) / len(intensities) if intensities else 0.0

            result[symptom_name][ingredient] = IngredientSymptomMetrics(
                exposures=a,
                trigger_rate=round(trigger_rate, 4),
                base_rate=round(base_rate, 4),
                fishers_p_value=round(p_value, 6),
                average_intensity=round(avg_intensity, 2),
            )

    return result


def get_food_symptom_counts(
    food_logs: list[FoodLogEntry],
    symptom_logs: list[SymptomLogEntry],
    time_window_hours: float,
) -> tuple[dict[str, dict[str, list]], dict[str, int]]:
    """
    Returns:
        counts: symptom_name -> ingredient -> [co_occurrence_count, [intensities]]
        foods_in_windows: symptom_name -> distinct food events found across all windows
                          (needed for computing c in the contingency table)
    """
    counts: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(lambda: [0, []]))
    foods_in_windows: dict[str, int] = defaultdict(int)

    window_results: list[SymptomFoodWindowResult] = get_food_logs_within_time_window_before_symptoms(
        food_logs, symptom_logs, time_window_hours
    )

    # symptom_name -> food_object_id -> (ingredients_set, [intensities])
    # Python list slicing returns references to the same objects, so id() is a
    # stable, unique key for each food log entry within this call even if two
    # entries share the same timestamp (e.g. three dishes logged at 18:00).
    seen: dict[str, dict[int, tuple[set, list]]] = defaultdict(dict)

    for window_result in window_results:
        symp = window_result.symptom_log
        s_name = symp.symptom_name

        for food in window_result.food_logs:
            key = id(food)
            if key not in seen[s_name]:
                seen[s_name][key] = (set(food.ingredients), [])
            seen[s_name][key][1].append(symp.intensity)

    counts: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(lambda: [0, []]))
    foods_in_windows: dict[str, int] = defaultdict(int)

    for s_name, food_map in seen.items():
        foods_in_windows[s_name] = len(food_map)
        for _ts, (ingredients, intensities) in food_map.items():
            for ingredient in ingredients:
                entry = counts[s_name][ingredient]
                entry[0] += 1
                entry[1].extend(intensities)

    return counts, foods_in_windows
