"""Picks a user's regular foods, builds 60 days of MealLogs + skipped days"""

import random
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from scripts.mock_users.foods import FOODS_BY_SLOT
from scripts.mock_users.shapes import MealLog, MockFood

LOCAL_TZ = ZoneInfo("America/New_York")  # meal times are picked in local time, then stored as UTC

# How many foods a user regularly eats from each slot (min, max). Small sets mean lots of repeats.
REGULAR_FOODS_PER_SLOT = {"breakfast": (2, 3), "lunch": (3, 4), "dinner": (4, 5), "snack": (2, 3), "drink": (2, 3)}

# Local time window (start, end) for each slot
SLOT_WINDOWS = {
    "breakfast": (time(7, 0), time(9, 30)),
    "lunch": (time(11, 30), time(14, 0)),
    "snack": (time(15, 0), time(17, 0)),
    "dinner": (time(17, 30), time(20, 30)),
    "drink": (time(18, 0), time(22, 0)),
}

# How likely a slot is picked on a given day (a user logs for that day)
SLOT_WEIGHTS = {"breakfast": 0.8, "lunch": 0.85, "snack": 0.4, "dinner": 0.95, "drink": 0.35}

MEALS_PER_DAY_WEIGHTS = {1: 0.1, 2: 0.3, 3: 0.45, 4: 0.15}
DEFAULT_DAYS = 60
DEFAULT_SKIP_RATE = 0.1


def pick_regular_foods(rng: random.Random) -> dict[str, list[MockFood]]:
    """Pick the foods this user repeats, per slot. The first food in each list is their favorite."""
    regular = {}
    for slot, (low, high) in REGULAR_FOODS_PER_SLOT.items():
        regular[slot] = rng.sample(FOODS_BY_SLOT[slot], rng.randint(low, high))
    return regular


def _pick_slots(rng: random.Random, count: int) -> list[str]:
    """Pick `count` different slots for one day, favoring the main meals."""
    remaining = dict(SLOT_WEIGHTS)
    picked = []
    for _ in range(count):
        slot = rng.choices(list(remaining), weights=list(remaining.values()))[0]
        picked.append(slot)
        del remaining[slot]
    return picked


def _random_time(rng: random.Random, day: date, slot: str) -> datetime:
    start, end = SLOT_WINDOWS[slot]
    start_min = start.hour * 60 + start.minute
    minute = rng.randint(start_min, end.hour * 60 + end.minute)
    local = datetime.combine(day, time()) + timedelta(minutes=minute)
    return local.replace(tzinfo=LOCAL_TZ).astimezone(timezone.utc)


def build_meals(
    rng: random.Random,
    regular_foods: dict[str, list[MockFood]],
    end_date: date,
    days: int = DEFAULT_DAYS,
    skip_rate: float = DEFAULT_SKIP_RATE,
) -> tuple[list[MealLog], list[date]]:
    """Build `days` days of meals ending on `end_date` (local dates). Returns (meals sorted by time, skipped days)."""
    meals: list[MealLog] = []
    skipped: list[date] = []
    counts = list(MEALS_PER_DAY_WEIGHTS)
    for offset in range(days - 1, -1, -1):
        day = end_date - timedelta(days=offset)
        if rng.random() < skip_rate:
            skipped.append(day)
            continue
        count = rng.choices(counts, weights=list(MEALS_PER_DAY_WEIGHTS.values()))[0]
        for slot in _pick_slots(rng, count):
            foods = regular_foods[slot]
            # Favorites get eaten more often: weights 1, 1/2, 1/3, ...
            food = rng.choices(foods, weights=[1 / (i + 1) for i in range(len(foods))])[0]
            meals.append(MealLog(food_name=food.name, timestamp=_random_time(rng, day, slot)))
    meals.sort(key=lambda m: m.timestamp)
    return meals, skipped
