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


@dataclass
class IngredientSymptomMetrics:
    trigger_rate: float       # P(ingredient | symptom)
    base_rate: float          # P(ingredient overall)
    relative_risk: float      # trigger_rate / base_rate
    fishers_p_value: float    # one-sided Fisher's exact p-value
    average_intensity: float  # mean symptom intensity when ingredient present
