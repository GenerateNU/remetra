"""Fixed values for model v2, from docs/model-v2-draft.md (Starting values)."""

import math

from models.symptom_family import SymptomFamily

P0 = 0.04

DAILY_BACKGROUND = {
    SymptomFamily.GI: 0.20,
    SymptomFamily.SKIN: 0.11,
    SymptomFamily.HEAD: 0.15,
}

INITIAL_LOG_ODDS = math.log(P0 / (1 - P0))

BACKGROUND_PRIOR_HOURS = 168

# s_f: chance a real trigger causes a reaction in the family from one full serving
REACTION_CHANCE = {
    SymptomFamily.GI: 0.40,
    SymptomFamily.SKIN: 0.30,
    SymptomFamily.HEAD: 0.25,
}


# T_f: meal lookback window per family (hours)
LOOKBACK_HOURS = {
    SymptomFamily.GI: 36,
    SymptomFamily.HEAD: 36,
    SymptomFamily.SKIN: 48,
}

# Timing curve parameters: (median_hours, spread)
# GI and HEAD use a single log-normal; SKIN mixes an early and a late curve
TIMING_PARAMS = {
    SymptomFamily.GI: [(4, 0.8)],
    SymptomFamily.HEAD: [(8, 0.8)],
    SymptomFamily.SKIN: [(1, 0.7), (24, 0.5)],
}

# SKIN mixing weight: 50% early, 50% late
SKIN_EARLY_WEIGHT = 0.5


def initial_background_rate(family: SymptomFamily) -> float:
    """Hourly background rate implied by the daily chance of the family's symptoms."""
    return -math.log(1 - DAILY_BACKGROUND[family]) / 24


def background_rate(family: SymptomFamily, background_total: float, hours_observed: float) -> float:
    """Background rate per hour, treating the starting rate as one week of observation."""
    prior_rate = initial_background_rate(family)
    return (background_total + prior_rate * BACKGROUND_PRIOR_HOURS) / (hours_observed + BACKGROUND_PRIOR_HOURS)
