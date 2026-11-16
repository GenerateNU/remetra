"""Pure math for model v2: meal strength and the timing curve. No database access."""

import math

from analysis.model_constants import REACTION_CHANCE
from models.symptom_family import SymptomFamily


def meal_strength(family: SymptomFamily, exposure: float) -> float:
    """Expected number of `family` reactions from one serving if the component is a real trigger.

    a_{c,f} = -ln(1 - s_f * e_c), where s_f is the family's reaction chance and e_c is the exposure (0 to 1).
    Raises ValueError if exposure is outside 0 to 1.
    """
    if not 0 <= exposure <= 1:
        raise ValueError(f"exposure must be between 0 and 1, got {exposure}")
    return -math.log(1 - REACTION_CHANCE[family] * exposure)
