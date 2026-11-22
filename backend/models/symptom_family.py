"""Symptom families. The single enum shared by symptom routing and the per-family model tables.

A symptom's family is never stored on the symptom: services.symptom_routing.route_symptom computes it
from location and sensation (rules in data/symptom_routing.yaml).
"""

import enum


class SymptomFamily(enum.StrEnum):
    """GI, skin, head, or other. OTHER symptoms are routed to the model but have no family confidences."""

    GI = "gi"
    SKIN = "skin"
    HEAD = "head"
    OTHER = "other"


# Families the model keeps confidences and background totals for
MODELED_FAMILIES: tuple[SymptomFamily, ...] = (SymptomFamily.GI, SymptomFamily.SKIN, SymptomFamily.HEAD)

# SQL literal list for CHECK constraints on family columns
FAMILY_VALUES = ", ".join(f"'{family}'" for family in MODELED_FAMILIES)  # 'gi', 'skin', 'head'
