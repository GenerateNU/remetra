"""Meal generation: repeatable, 1-4 meals a day at plausible times, repeated foods, skipped days."""

import random
from collections import Counter
from datetime import date

from scripts.mock_users.meals import LOCAL_TZ, REGULAR_FOODS_PER_SLOT, build_meals, pick_regular_foods

END = date(2026, 11, 1)


def _generate(seed, **kwargs):
    rng = random.Random(seed)
    regular = pick_regular_foods(rng)
    meals, skipped = build_meals(rng, regular, END, **kwargs)
    return regular, meals, skipped


def _local_dates(meals):
    return Counter(m.timestamp.astimezone(LOCAL_TZ).date() for m in meals)


def test_same_seed_gives_same_meals():
    assert _generate(42) == _generate(42)


def test_different_seeds_give_different_meals():
    assert _generate(1)[1] != _generate(2)[1]


def test_covers_requested_days_ending_on_end_date():
    _, meals, skipped = _generate(7)
    meal_days = _local_dates(meals)

    assert len(meal_days) + len(skipped) == 60
    assert set(meal_days).isdisjoint(skipped)
    assert max([*meal_days, *skipped]) == END
    assert min([*meal_days, *skipped]) == date(2026, 9, 3)


def test_one_to_four_meals_on_each_logged_day():
    _, meals, _ = _generate(7)

    assert all(1 <= count <= 4 for count in _local_dates(meals).values())


def test_meals_are_at_plausible_local_times_and_sorted():
    _, meals, _ = _generate(7)

    assert all(7 <= m.timestamp.astimezone(LOCAL_TZ).hour <= 22 for m in meals)
    assert meals == sorted(meals, key=lambda m: m.timestamp)


def test_meals_only_use_the_users_regular_foods():
    regular, meals, _ = _generate(7)
    regular_names = {food.name for foods in regular.values() for food in foods}
    max_regular = sum(high for _, high in REGULAR_FOODS_PER_SLOT.values())

    assert {m.food_name for m in meals} <= regular_names
    assert len(regular_names) <= max_regular
    # ~60 days of meals from a small set means every regular food is eaten many times on average
    assert len(meals) / len(regular_names) >= 5


def test_skip_rate_zero_skips_nothing():
    _, _, skipped = _generate(7, skip_rate=0)

    assert skipped == []


def test_skip_rate_one_skips_every_day():
    _, meals, skipped = _generate(7, skip_rate=1)

    assert meals == []
    assert len(skipped) == 60


def test_default_skip_rate_skips_some_days():
    _, _, skipped = _generate(7)

    assert 0 < len(skipped) < 60


def test_zero_days_gives_nothing():
    _, meals, skipped = _generate(7, days=0)

    assert meals == []
    assert skipped == []
