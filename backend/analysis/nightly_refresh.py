from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from analysis.model_constants import DEFAULT_LOOKBACK_HOURS, LOOKBACK_HOURS
from models.symptom_family import SymptomFamily
from schemas.food_log import FoodLogResponse
from schemas.symptom_log import SymptomLogResponse


def lookback(family: SymptomFamily | None) -> timedelta:
    """How far before a symptom a meal can still have caused it (LOOKBACK_HOURS, or the default if unmodeled)."""
    return timedelta(hours=LOOKBACK_HOURS.get(family, DEFAULT_LOOKBACK_HOURS))


@dataclass
class SymptomMealMap:
    food_log: FoodLogResponse
    symptoms: dict[UUID, timedelta]
    food_time: datetime


@dataclass(frozen=True)
class PairTiming:
    """Timing curve weight for one food log - symptom log pair."""

    food_log_id: UUID
    symptom_log_id: UUID
    time_elapsed: timedelta
    weight: float


def nightly_refresh(
    new_meals: list[FoodLogResponse],
    new_symptoms: list[SymptomLogResponse],
    now: datetime,
    last_update: datetime,
) -> list[PairTiming]:
    """Return the timing curve weight for every linked food log - symptom log pair."""
    symptoms_by_id = {symptom.id: symptom for symptom in new_symptoms}
    results = []
    for meal_map in symptom_meal_map(new_meals, new_symptoms, now, last_update):
        for symptom_log_id, time_elapsed in meal_map.symptoms.items():
            weight = update(
                food_log_id=meal_map.food_log.id,
                symptom_log_id=symptom_log_id,
                time_elapsed=time_elapsed,
                family=symptoms_by_id[symptom_log_id].family,
            )
            results.append(PairTiming(meal_map.food_log.id, symptom_log_id, time_elapsed, weight))

    return results


def update(
    food_log_id: UUID,
    symptom_log_id: UUID,
    time_elapsed: timedelta,
    family: str,
) -> float:
    """Return how strongly the timing links this meal to this symptom."""
    pass


def symptom_meal_map(
    new_meals: list[FoodLogResponse],
    new_symptoms: list[SymptomLogResponse],
    now: datetime,
    last_update: datetime | None = None,
):
    """Map each symptom to the meals that occurred within the relevant lookback window."""
    meal_dict = {}
    for symptom in new_symptoms:
        if last_update is None:
            in_window = now - timedelta(hours=24) <= symptom.timestamp <= now
        else:
            in_window = last_update < symptom.timestamp <= now
        if in_window:
            lookback_end = symptom.timestamp - lookback(symptom.family)

            for meal in new_meals:
                if meal.timestamp >= lookback_end and meal.timestamp <= symptom.timestamp:
                    if meal.id not in meal_dict:
                        meal_dict[meal.id] = []
                    meal_dict[meal.id].append(symptom)

    meal_maps = []
    for meal in new_meals:
        symptoms = {}
        for symptom in meal_dict.get(meal.id, []):
            symptoms[symptom.id] = symptom.timestamp - meal.timestamp
        meal_maps.append(SymptomMealMap(food_log=meal, symptoms=symptoms, food_time=meal.timestamp))

    return meal_maps
