from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from models.metrics import Metrics
from schemas.food_log import FoodLogResponse
from schemas.symptom_log import SymptomLogResponse


@dataclass
class SymptomMealMap:
    food_log: FoodLogResponse
    symptoms: dict[UUID, timedelta]
    food_time: datetime


def nightly_refresh(
    new_meals: list[FoodLogResponse],
    new_symptoms: list[SymptomLogResponse],
    metrics: list[Metrics],
):
    # TODO later
    pass


def symptom_meal_map(
    new_meals: list[FoodLogResponse],
    new_symptoms: list[SymptomLogResponse],
    now: datetime,
):
    day_ago = now - timedelta(hours=24)
    meal_dict = {}
    for symptom in new_symptoms:
        if symptom.timestamp >= day_ago and symptom.timestamp <= now:
            lookback = 36
            if symptom.family == "SKIN":
                lookback = 48

            lookback_end = symptom.timestamp - timedelta(hours=lookback)

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
