"""Symptom generation: reactions only after trigger meals, inside the delay window, plus background noise."""

import random
from datetime import date, datetime, timedelta, timezone

from scripts.mock_users.meals import LOCAL_TZ, build_meals, pick_regular_foods
from scripts.mock_users.shapes import MealLog, MockFood, SymptomKind, Trigger
from scripts.mock_users.symptoms import BACKGROUND_SYMPTOMS, build_symptoms, planted_reactions, trigger_meals

END = date(2026, 11, 1)
LACTOSE = Trigger("lactose", 1, 6, SymptomKind("Cramping", "Abdomen"))
MILKY = MockFood("Mac and cheese", ["pasta", "cheese", "milk", "butter"])
PLAIN = MockFood("Quinoa salad", ["quinoa", "cucumber", "olive oil"])


def _meal(food, day, hour):
    return MealLog(food.name, datetime(2026, 10, day, hour, tzinfo=timezone.utc))


def _symptoms(seed, trigger=LACTOSE, rate=0.15, **kwargs):
    rng = random.Random(seed)
    regular = pick_regular_foods(rng)
    foods = [f for slot in regular.values() for f in slot]
    meals, skipped = build_meals(rng, regular, END, **kwargs)
    symptoms = build_symptoms(rng, meals, foods, trigger, rate, END, kwargs.get("days", 60), skipped)
    return foods, meals, skipped, symptoms


def test_trigger_meals_uses_taxonomy_lookup():
    meals = [_meal(MILKY, 1, 12), _meal(PLAIN, 1, 18)]

    assert trigger_meals(meals, [MILKY, PLAIN], "lactose") == [meals[0]]


def test_one_reaction_per_trigger_meal_inside_delay_window():
    meals = [_meal(MILKY, d, 12) for d in range(1, 11)] + [_meal(PLAIN, d, 18) for d in range(1, 11)]

    reactions = planted_reactions(random.Random(1), meals, [MILKY, PLAIN], LACTOSE)

    assert len(reactions) == 10
    for meal, reaction in zip(meals[:10], reactions):
        assert meal.timestamp + timedelta(hours=1) <= reaction.timestamp <= meal.timestamp + timedelta(hours=6)
        assert reaction.planted and reaction.symptom == LACTOSE.symptom


def test_reaction_delay_varies_instead_of_fixed_offset():
    meals = [_meal(MILKY, d, 12) for d in range(1, 11)]

    reactions = planted_reactions(random.Random(1), meals, [MILKY], LACTOSE)

    assert len({r.timestamp - m.timestamp for m, r in zip(meals, reactions)}) > 1


def test_no_reactions_when_trigger_never_eaten():
    meals = [_meal(PLAIN, d, 12) for d in range(1, 11)]

    assert planted_reactions(random.Random(1), meals, [PLAIN], LACTOSE) == []


def test_no_trigger_user_has_only_background_symptoms():
    *_, symptoms = _symptoms(3, trigger=None)

    assert symptoms
    assert not any(s.planted for s in symptoms)


def test_every_planted_reaction_follows_a_trigger_meal():
    foods, meals, _, symptoms = _symptoms(3)
    eaten = trigger_meals(meals, foods, LACTOSE.component)

    for s in (s for s in symptoms if s.planted):
        assert any(timedelta(hours=1) <= s.timestamp - m.timestamp <= timedelta(hours=6) for m in eaten)


def test_background_rate_zero_gives_only_planted():
    *_, symptoms = _symptoms(3, rate=0)

    assert all(s.planted for s in symptoms)


def test_background_rate_is_roughly_respected():
    *_, symptoms = _symptoms(3, trigger=None, rate=0.5, days=400, skip_rate=0)

    assert 150 <= len(symptoms) <= 250  # ~200 expected


def test_no_symptoms_on_skipped_days_or_after_end_date():
    _, _, skipped, symptoms = _symptoms(3, skip_rate=0.3)
    days = {s.timestamp.astimezone(LOCAL_TZ).date() for s in symptoms}

    assert skipped
    assert days.isdisjoint(skipped)
    assert max(days) <= END


def test_symptoms_use_known_kinds_and_valid_intensity_and_are_sorted():
    *_, symptoms = _symptoms(3)

    assert all(s.symptom in BACKGROUND_SYMPTOMS for s in symptoms)
    assert all(1 <= s.intensity <= 10 for s in symptoms)
    assert symptoms == sorted(symptoms, key=lambda s: s.timestamp)


def test_same_seed_gives_same_symptoms():
    assert _symptoms(5) == _symptoms(5)
