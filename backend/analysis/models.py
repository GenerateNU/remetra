import datetime
from dataclasses import dataclass


@dataclass
class FoodLogEntry:
    timestamp: datetime
    ingredients: list[str] 
    servings: int

@dataclass
class SymptomLogEntry:
    timestamp: datetime
    symptom_name: str       
    intensity: int          