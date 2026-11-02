"""Builds a user's symptoms: planted reactions after trigger meals, plus background symptoms."""

import math
import random
from datetime import date, datetime, time, timedelta, timezone

from scripts.mock_users.meals import LOCAL_TZ
from scripts.mock_users.shapes import MealLog, MockFood, SymptomEvent, SymptomKind, Trigger
from services.taxonomy_service import TaxonomyService

# Symptoms anyone might log on a random day, unrelated to food. Includes the trigger symptoms,
# so a planted reaction's symptom type alone doesn't give the trigger away.
BACKGROUND_SYMPTOMS = [
    SymptomKind("Fatigue", "Whole Body"),
    SymptomKind("Aching", "Joints (Multiple)"),
    SymptomKind("Stiffness", "Lower Back"),
    SymptomKind("Itching", "Skin"),
    SymptomKind("Throbbing", "Head"),
    SymptomKind("Bloating", "Abdomen"),
    SymptomKind("Cramping", "Abdomen"),
]

PLANTED_INTENSITY = (5, 9)
PLANTED_DURATION_MINUTES = (60, 360)
BACKGROUND_INTENSITY = (1, 6)
BACKGROUND_DURATION_MINUTES = (15, 180)
BACKGROUND_WINDOW = (time(6, 0), time(23, 0))  # local time background symptoms can happen


def trigger_meals(meals: list[MealLog], foods: list[MockFood], component: str) -> list[MealLog]:
    """Meals whose food contains `component` at any level, according to the taxonomy lookup."""
    service = TaxonomyService()
    has_component = {
        food.name: any(component in match.components for match in service.lookup_many(food.ingredients))
        for food in foods
    }
    return [meal for meal in meals if has_component.get(meal.food_name, False)]


def planted_reactions(
    rng: random.Random, meals: list[MealLog], foods: list[MockFood], trigger: Trigger
) -> list[SymptomEvent]:
    """One reaction per trigger meal, at a random time inside the trigger's delay window."""
    events = []
    for meal in trigger_meals(meals, foods, trigger.component):
        delay = rng.uniform(trigger.delay_min_hours, trigger.delay_max_hours)
        events.append(
            SymptomEvent(
                symptom=trigger.symptom,
                intensity=rng.randint(*PLANTED_INTENSITY),
                timestamp=meal.timestamp + timedelta(hours=delay),
                duration_minutes=rng.randint(*PLANTED_DURATION_MINUTES),
                planted=True,
            )
        )
    return events


def _poisson(rng: random.Random, rate: float) -> int:
    """Number of events in one day for an average of `rate` per day (Knuth's method)."""
    limit, count, product = math.exp(-rate), 0, rng.random()
    while product > limit:
        count += 1
        product *= rng.random()
    return count


def background_symptoms(rng: random.Random, end_date: date, days: int, rate: float) -> list[SymptomEvent]:
    """Symptoms unrelated to food, `rate` per day on average, at random local times."""
    start, end = BACKGROUND_WINDOW
    start_min, end_min = start.hour * 60 + start.minute, end.hour * 60 + end.minute
    events = []
    for offset in range(days - 1, -1, -1):
        day = end_date - timedelta(days=offset)
        for _ in range(_poisson(rng, rate)):
            local = datetime.combine(day, time()) + timedelta(minutes=rng.randint(start_min, end_min))
            events.append(
                SymptomEvent(
                    symptom=rng.choice(BACKGROUND_SYMPTOMS),
                    intensity=rng.randint(*BACKGROUND_INTENSITY),
                    timestamp=local.replace(tzinfo=LOCAL_TZ).astimezone(timezone.utc),
                    duration_minutes=rng.randint(*BACKGROUND_DURATION_MINUTES),
                    planted=False,
                )
            )
    return events


def build_symptoms(
    rng: random.Random,
    meals: list[MealLog],
    foods: list[MockFood],
    trigger: Trigger | None,
    background_rate: float,
    end_date: date,
    days: int,
    skipped_days: list[date],
) -> list[SymptomEvent]:
    """All of a user's logged symptoms, sorted by time. Nothing is logged on skipped days."""
    events = planted_reactions(rng, meals, foods, trigger) if trigger else []
    events += background_symptoms(rng, end_date, days, background_rate)
    skipped = set(skipped_days)
    # A reaction to the last day's dinner can land after end_date; drop it with the skipped days
    events = [e for e in events if (d := e.timestamp.astimezone(LOCAL_TZ).date()) not in skipped and d <= end_date]
    events.sort(key=lambda e: e.timestamp)
    return events
