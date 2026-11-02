from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from enum import Enum
from typing import Callable, Protocol
from zoneinfo import ZoneInfo

from backend.analysis.models import FoodLogEntry, SymptomLogEntry

# from backend.services.taxonomy_service import IngredientMatch
from backend.schemas.symptom_log import SymptomRoute

UNKNOWN = "unknown"
BIN_HOURS = 3
REACTION_WINDOW = timedelta(hours=36)
BinKey = tuple[date, int]


class BinStatus(str, Enum):
    USABLE = "usable"
    PENDING = "pending"
    UNUSABLE = "unusable"


class IngredientMatchLike(Protocol):
    ingredient_id: str
    components: dict[str, int]


@dataclass
class TimelineBin:
    start: datetime
    components: dict[str, int]
    symptoms: dict[str, int]
    status: BinStatus
    unmatched_ingredients: set[str]


def _bin_status(start: datetime, has_food: bool, checked_in: set[date], tz: ZoneInfo, now: datetime) -> BinStatus:
    # determine the BinStatus based on the provided parameters
    if not has_food:
        return BinStatus.USABLE

    start_utc = start.astimezone(timezone.utc)
    end_utc = start_utc + REACTION_WINDOW
    today = now.astimezone(tz).date()
    day = start_utc.astimezone(tz).date()
    last_day = (end_utc - timedelta(microseconds=1)).astimezone(tz).date()

    while day <= last_day:
        if day < today and day not in checked_in:
            return BinStatus.UNUSABLE
        day += timedelta(days=1)

    if now < end_utc:
        return BinStatus.PENDING

    return BinStatus.USABLE


def _bin_key(bin_date: datetime, tz: ZoneInfo) -> BinKey:
    local_date = bin_date.astimezone(tz)
    return (local_date.date(), local_date.hour // BIN_HOURS)


def _checked_in_days(symptom_logs: list[SymptomLogEntry], no_symptom_days: list[date], tz: ZoneInfo) -> set[date]:
    checked_in: set[date] = set()
    for symptom in symptom_logs:
        local_date = symptom.timestamp.astimezone(tz).date()
        checked_in.add(local_date)
    for day in no_symptom_days:
        checked_in.add(day)
    return checked_in


def _bin_start(day: date, index: int, tz: ZoneInfo) -> datetime:
    return datetime.combine(day, time(index * BIN_HOURS), tzinfo=tz)


def _in_range(bin_key: BinKey, start_date: date, end_date: date) -> bool:
    return start_date <= bin_key[0] <= end_date


def build_timeline(
    food_logs: list[FoodLogEntry],
    symptom_logs: list[SymptomLogEntry],
    no_symptom_days: list[date],
    tz: ZoneInfo,
    start_date: date,
    end_date: date,
    now: datetime,
    lookup: Callable[[str], IngredientMatchLike],
    route: Callable[[str, str], SymptomRoute],
) -> list[TimelineBin]:

    food_keys: set[BinKey] = set()
    components: dict[BinKey, dict[str, int]] = {}
    unmatched: dict[BinKey, set[str]] = {}
    for entry in food_logs:
        key = _bin_key(entry.timestamp, tz)
        if not _in_range(key, start_date, end_date):
            continue
        food_keys.add(key)
        for ingredient in entry.ingredients:
            match = lookup(ingredient)
            if match.ingredient_id == UNKNOWN:
                unmatched.setdefault(key, set()).add(ingredient)
                continue
            bucket = components.setdefault(key, {})
            for component, level in match.components.items():
                bucket[component] = max(bucket.get(component, level), level)

    symptoms: dict[BinKey, dict[str, int]] = {}
    for symptom in symptom_logs:
        key = _bin_key(symptom.timestamp, tz)
        if not _in_range(key, start_date, end_date):
            continue
        result = route(symptom.sensation, symptom.location)
        if result.route != "model" or result.family is None:
            continue
        family = result.family
        bucket = symptoms.setdefault(key, {})
        bucket[family] = max(bucket.get(family, symptom.intensity), symptom.intensity)

    checked_in = _checked_in_days(symptom_logs, no_symptom_days, tz)

    bins: list[TimelineBin] = []
    for key in sorted(food_keys | symptoms.keys()):
        day, index = key
        start = _bin_start(day, index, tz)
        bin_components = components.get(key, {})
        bin_symptoms = symptoms.get(key, {})
        bins.append(
            TimelineBin(
                start=start,
                components=bin_components,
                symptoms=bin_symptoms,
                status=_bin_status(start, key in food_keys, checked_in, tz, now),
                unmatched_ingredients=unmatched.get(key, set()),
            )
        )
    return bins
