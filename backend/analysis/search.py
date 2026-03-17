"""Binary-search utilities for food/symptom time-window lookups."""

from bisect import bisect_left
from dataclasses import dataclass
from datetime import timedelta

from analysis.models import FoodLogEntry, SymptomLogEntry


@dataclass
class SymptomFoodWindowResult:
    """Pair a symptom log with the foods logged shortly before it."""

    symptom_log: SymptomLogEntry
    food_logs: list[FoodLogEntry]


def get_food_logs_within_time_window_before_symptoms(
    food_logs: list[FoodLogEntry],
    symptom_logs: list[SymptomLogEntry],
    time_window_hours: float,
) -> list[SymptomFoodWindowResult]:
    """Return food logs in a time window before each symptom log.

    The returned foods are those with timestamps in:
    [symptom_timestamp - time_window_hours, symptom_timestamp)
    """

    if time_window_hours < 0:
        raise ValueError("time_window_hours must be >= 0")

    window_delta = timedelta(hours=time_window_hours)

    sorted_food_logs = sorted(food_logs, key=lambda log: log.timestamp)
    sorted_food_timestamps = [log.timestamp for log in sorted_food_logs]

    results: list[SymptomFoodWindowResult] = []
    for symptom_log in symptom_logs:
        window_start = symptom_log.timestamp - window_delta

        start_index = bisect_left(sorted_food_timestamps, window_start)
        end_index = bisect_left(sorted_food_timestamps, symptom_log.timestamp)

        results.append(
            SymptomFoodWindowResult(
                symptom_log=symptom_log,
                food_logs=sorted_food_logs[start_index:end_index],
            )
        )

    return results
