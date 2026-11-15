"""Symptom families the model groups symptoms into. Shared by every table that stores a family."""

import enum


class SymptomFamily(enum.StrEnum):
    """GI, skin, or head. A symptom with no family (NULL) isn't modeled and the update skips it"""

    GI = "GI"
    SKIN = "SKIN"
    HEAD = "HEAD"
