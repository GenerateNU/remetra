"""Symptom families the model groups symptoms into. Shared by every table that stores a family."""

import enum


class SymptomFamily(enum.StrEnum):
    """GI, skin, or head. A symptom with no family (NULL) isn't modeled and the update skips it"""

    GI = "GI"
    SKIN = "SKIN"
    HEAD = "HEAD"


# SQL literal list for CHECK constraints on family columns
FAMILY_VALUES = ", ".join(f"'{family}'" for family in SymptomFamily)  # 'GI', 'SKIN', 'HEAD'


# Location → family. Locations come from frontend/src/types/symptomOptions.ts and are compared
# case-insensitively. Locations not listed here (joints, back, limbs, ...) aren't modeled.
_LOCATION_FAMILIES: dict[str, SymptomFamily] = {
    "abdomen": SymptomFamily.GI,
    "skin": SymptomFamily.SKIN,
    "head": SymptomFamily.HEAD,
    "eyes": SymptomFamily.HEAD,
}

# Sensations that point to a family wherever they're felt. Checked before the location,
# so "Bloating — Whole Body" is GI and "Itching — Hands / Fingers" is SKIN.
_SENSATION_FAMILIES: dict[str, SymptomFamily] = {
    "bloating": SymptomFamily.GI,
    "itching": SymptomFamily.SKIN,
}

# (location, sensation) pairs that override both tables above.
_PAIR_FAMILIES: dict[tuple[str, str], SymptomFamily | None] = {
    ("throat", "burning"): SymptomFamily.GI,  # reflux
    ("eyes", "itching"): None,  # allergic, not skin or head
}


def family_for_symptom(location: str | None, sensation: str | None) -> SymptomFamily | None:
    """Return the family a symptom belongs to, or None if the model doesn't cover it."""
    loc = (location or "").strip().lower()
    sens = (sensation or "").strip().lower()
    if (loc, sens) in _PAIR_FAMILIES:
        return _PAIR_FAMILIES[(loc, sens)]
    return _SENSATION_FAMILIES.get(sens) or _LOCATION_FAMILIES.get(loc)
