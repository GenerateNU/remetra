"""Safety filters for the daily ingredient pool; Ranking may reorder or trim `eligible`.

lookup = taxonomy_service.lookup
context = build_user_context(user.disease, food_logs, lookup, now)
eligible = eligible_ingredients(taxonomy_service.data, context, washout)
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from analysis.models import FoodLogEntry
from schemas.symptom_log import WashoutStatus
from services.taxonomy_service import IngredientMatch, TaxonomyData

Lookup = Callable[[str | None], IngredientMatch]

ALLERGEN_HISTORY_DAYS = 30
_CELIAC_TERMS = ("celiac", "coeliac")


@dataclass(frozen=True)
class UserContext:
    """safety filters user knowledge

    disease is User.disease, components_eaten_last_30_days holds every
    component id at level > 0 in the user's food logs in the last 30 days
    """

    disease: list[str]
    components_eaten_last_30_days: set[str]


def build_user_context(
    disease: list[str] | None,
    food_logs: list[FoodLogEntry],
    lookup: Lookup,
    now: datetime,
) -> UserContext:
    return UserContext(
        disease=list(disease or []),
        components_eaten_last_30_days=components_eaten_since(
            food_logs, lookup, since=now - timedelta(days=ALLERGEN_HISTORY_DAYS), now=now
        ),
    )


def components_in_log(ingredients: list[str], lookup: Lookup) -> set[str]:
    """Component ids at level > 0 across one food log's ingredient strings."""
    present: set[str] = set()
    for name in ingredients:
        if not name:
            continue
        present.update(component for component, level in lookup(str(name)).components.items() if level > 0)
    return present


def components_eaten_since(
    food_logs: list[FoodLogEntry],
    lookup: Lookup,
    since: datetime,
    now: datetime,
) -> set[str]:
    """Component ids eaten in food logs from `since` through `now`, inclusive."""
    start, end = _as_utc(since), _as_utc(now)
    eaten: set[str] = set()
    for log in food_logs:
        if start <= _as_utc(log.timestamp) <= end:
            eaten.update(components_in_log(log.ingredients, lookup))
    return eaten


def eligible_ingredients(
    taxonomy: TaxonomyData,
    user_context: UserContext,
    washout: WashoutStatus,
) -> list[str]:
    """sorted ingredient ids that pass the washout, celiac and allergen rules"""
    celiac = has_celiac(user_context.disease)
    eaten = user_context.components_eaten_last_30_days
    kept: list[str] = []
    for ingredient_id, row in taxonomy.ingredients.items():
        if washout.active and not _is_elimination_base(row):
            continue
        levels = _levels(taxonomy, ingredient_id)
        if celiac and levels.get("gluten", 0) > 0:
            continue
        if any(component not in eaten for component in levels.keys() & taxonomy.allergen_components):
            continue
        kept.append(ingredient_id)
    return sorted(kept)


def has_celiac(disease: list[str] | None) -> bool:
    """matches celiac anywhere in an entry, any case"""
    return any(term in entry.lower() for entry in disease or [] for term in _CELIAC_TERMS)


def _levels(taxonomy: TaxonomyData, ingredient_id: str) -> dict[str, int]:
    """component id -> level from ingredient_components.csv"""
    return {row["component"]: int(row["level"]) for row in taxonomy.pairs.get(ingredient_id, [])}


def _is_elimination_base(row: dict) -> bool:
    return str(row.get("elimination_base", "")).strip().lower() == "true"


def _as_utc(timestamp: datetime) -> datetime:
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=timezone.utc)
    return timestamp.astimezone(timezone.utc)
