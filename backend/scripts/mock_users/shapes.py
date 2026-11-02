"""
Shape of the generated data, shared by the generator and the code that saves it.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

import yaml

USER_TYPES_PATH = Path(__file__).resolve().parent / "user_types.yaml"
USERNAME_PREFIX = "mock_"


@dataclass(frozen=True)
class SymptomKind:
    sensation: str  # must be one of the app's sensation options
    location: str  # must be one of the app's location options


@dataclass(frozen=True)
class Trigger:
    component: str  # component id from data/taxonomy/components.yaml
    delay_min_hours: float
    delay_max_hours: float
    symptom: SymptomKind


@dataclass(frozen=True)
class UserType:
    name: str
    trigger: Trigger | None  # None for no-trigger users


@dataclass(frozen=True)
class MockFood:
    name: str
    ingredients: list[str]  # canonical ingredient names that TaxonomyService.lookup resolves


@dataclass(frozen=True)
class MealLog:
    food_name: str  # matches a MockFood.name for the same user
    timestamp: datetime  # timezone-aware, UTC


@dataclass(frozen=True)
class SymptomEvent:
    symptom: SymptomKind
    intensity: int  # 1-10
    timestamp: datetime  # timezone-aware, UTC
    duration_minutes: int
    planted: bool  # True if caused by the user's trigger, False for background symptoms


@dataclass
class MockUserData:
    username: str  # always starts with USERNAME_PREFIX
    user_type: UserType
    foods: list[MockFood] = field(default_factory=list)
    meals: list[MealLog] = field(default_factory=list)
    symptoms: list[SymptomEvent] = field(default_factory=list)
    skipped_days: list[date] = field(default_factory=list)


def load_user_types(path: Path = USER_TYPES_PATH) -> tuple[dict[str, UserType], float]:
    """Return (user type name -> UserType, background symptoms per day)."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    types = {}
    for name, spec in raw["user_types"].items():
        trigger = None
        if spec.get("trigger"):
            t = spec["trigger"]
            trigger = Trigger(
                component=t["component"],
                delay_min_hours=float(t["delay_hours"][0]),
                delay_max_hours=float(t["delay_hours"][1]),
                symptom=SymptomKind(**t["symptom"]),
            )
        types[name] = UserType(name=name, trigger=trigger)
    return types, float(raw["background_symptoms_per_day"])
