"""Weekly label rules from docs/model-v2-draft.md (Labels). Pure functions, no database access."""

import enum
import math
from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

COMPONENTS_YAML = Path(__file__).resolve().parent.parent / "data" / "taxonomy" / "components.yaml"

# Looks fine: Q <= 0.05 after at least 3 meaningful exposures
LOOKS_FINE_MAX = 0.05
LOOKS_FINE_MIN_EXPOSURES = 3
# Likely trigger: Q >= 0.90 (and a completed re-check)
LIKELY_TRIGGER_MIN = 0.90
# No clear food pattern: at least 60% look fine and nothing at Q >= 0.30
NO_PATTERN_FINE_SHARE = 0.60
NO_PATTERN_MAX = 0.30

# A meal exposes a component at a meaningful amount when e_{m,c} >= 0.34 ...
MEANINGFUL_EXPOSURE = 0.34
# ... and it only counts toward n_c once its 48 h window has passed
EXPOSURE_SETTLE_HOURS = 48
MAX_CONCENTRATION_LEVEL = 3


class Label(enum.StrEnum):
    LOOKS_FINE = "looks_fine"
    LIKELY_TRIGGER = "likely_trigger"
    STILL_LEARNING = "still_learning"


@dataclass(frozen=True)
class MergeGroup:
    """Always-together components that are labelled as one group, never member by member."""

    id: str
    members: tuple[str, ...]
    display_name: str


@lru_cache(maxsize=1)
def load_merge_groups(path: Path = COMPONENTS_YAML) -> tuple[MergeGroup, ...]:
    """Read merge_groups from components.yaml."""
    entries = yaml.safe_load(path.read_text(encoding="utf-8")).get("merge_groups") or []
    return tuple(MergeGroup(e["id"], tuple(e["members"]), e["display_name"]) for e in entries)


def to_probability(log_odds: float) -> float:
    """q = 1 / (1 + e^-l)."""
    return 1.0 / (1.0 + math.exp(-log_odds))


def combine(confidences: Iterable[float]) -> float:
    """Chance at least one is real: 1 - prod(1 - q). Gives Q_c from q_{c,f}, and Q_G from members' Q_c."""
    product = 1.0
    for q in confidences:
        product *= 1.0 - q
    return 1.0 - product


def meal_exposures(ingredients: Iterable[str], levels: dict[str, dict[str, int]]) -> dict[str, float]:
    """e_{m,c} = min(1, sum_i level_{i,c} / 3), assuming one standard serving of each ingredient.

    `levels` maps a lowercased ingredient name to {component slug: concentration level}. Unknown ingredients are
    skipped.
    """
    totals: dict[str, float] = {}
    for ingredient in ingredients:
        if not isinstance(ingredient, str):
            continue
        for slug, level in levels.get(ingredient.strip().lower(), {}).items():
            totals[slug] = totals.get(slug, 0.0) + level / MAX_CONCENTRATION_LEVEL
    return {slug: min(1.0, total) for slug, total in totals.items()}


def meaningful_components(exposures: dict[str, float]) -> set[str]:
    """Components the meal contains at a meaningful amount."""
    return {slug for slug, e in exposures.items() if e >= MEANINGFUL_EXPOSURE}


def label_for(confidence: float, exposure_count: int, recheck_completed: bool) -> Label:
    """Label one component or group from its confidence and exposure count.

    Not handled yet (needs the previously shown label, which nothing stores): a food that looked fine stays fine
    until Q rises above 0.30.
    """
    if confidence >= LIKELY_TRIGGER_MIN and recheck_completed:
        return Label.LIKELY_TRIGGER
    if confidence <= LOOKS_FINE_MAX and exposure_count >= LOOKS_FINE_MIN_EXPOSURES:
        return Label.LOOKS_FINE
    return Label.STILL_LEARNING


def is_no_clear_pattern(labelled: list[tuple[float, Label]]) -> bool:
    """At least 60% look fine and none has Q >= 0.30. False when nothing has been labelled yet."""
    if not labelled:
        return False
    fine = sum(1 for _, label in labelled if label == Label.LOOKS_FINE)
    return fine / len(labelled) >= NO_PATTERN_FINE_SHARE and all(q < NO_PATTERN_MAX for q, _ in labelled)
