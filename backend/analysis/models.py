from dataclasses import dataclass
from datetime import datetime


@dataclass
class FoodLogEntry:
    timestamp: datetime
    ingredients: list[str]


@dataclass
class SymptomLogEntry:
    timestamp: datetime
    symptom_name: str
    location: str
    sensation: str
    intensity: int
    duration: int | None = None
