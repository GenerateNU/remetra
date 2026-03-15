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
    intensity: int
    location: str = ("",)
    sensation: str = ("",)
    duration: int | None = None


@dataclass
class IngredientSymptomMetrics:
    exposures: int  # food events with this ingredient that preceded a symptom (a)
    trigger_rate: float  # P(symptom follows | ate ingredient) = a / ingredient_total
    base_rate: float  # P(symptom follows | did NOT eat ingredient) = c / (F - ingredient_total)
    fishers_p_value: float  # one-sided Fisher's exact test — probability this association is random chance
    average_intensity: float  # mean symptom intensity (1-10) across the exposures
