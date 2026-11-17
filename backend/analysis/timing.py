"""Pure math for model v2: meal strength, timing curves and evidence functions. No database access."""

import math
from uuid import UUID

from analysis.model_constants import (
    LOOKBACK_HOURS,
    REACTION_CHANCE,
    SKIN_EARLY_WEIGHT,
    TIMING_PARAMS,
)
from models.symptom_family import SymptomFamily


def _phi(x: float) -> float:
    """Standard normal CDF using math.erf."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _log_normal_pdf(delta: float, m: float, sigma: float) -> float:
    """Log-normal density g(delta; M, sigma)."""
    if delta <= 0:
        return 0.0
    z = (math.log(delta) - math.log(m)) / sigma
    return math.exp(-0.5 * z * z) / (delta * sigma * math.sqrt(2.0 * math.pi))


def _log_normal_cdf(delta: float, m: float, sigma: float) -> float:
    """Log-normal CDF G(delta; M, sigma)."""
    if delta <= 0:
        return 0.0
    return _phi((math.log(delta) - math.log(m)) / sigma)


def timing_density(family: SymptomFamily, delta: float) -> float:
    """k_f(delta): timing curve density at delta hours after eating. 0 outside (0, T_f]."""
    t_f = LOOKBACK_HOURS[family]
    if delta <= 0 or delta > t_f:
        return 0.0

    params = TIMING_PARAMS[family]
    if family == SymptomFamily.SKIN:
        m_early, s_early = params[0]
        m_late, s_late = params[1]
        numerator = (
            SKIN_EARLY_WEIGHT * _log_normal_pdf(delta, m_early, s_early)
            + (1 - SKIN_EARLY_WEIGHT) * _log_normal_pdf(delta, m_late, s_late)
        )
        denominator = (
            SKIN_EARLY_WEIGHT * _log_normal_cdf(t_f, m_early, s_early)
            + (1 - SKIN_EARLY_WEIGHT) * _log_normal_cdf(t_f, m_late, s_late)
        )
    else:
        m, sigma = params[0]
        numerator = _log_normal_pdf(delta, m, sigma)
        denominator = _log_normal_cdf(t_f, m, sigma)

    if denominator == 0:
        return 0.0
    return numerator / denominator


def timing_share(family: SymptomFamily, a: float, b: float) -> float:
    """K_f(a, b): share of the timing curve between a and b hours after eating."""
    t_f = LOOKBACK_HOURS[family]
    a = max(0.0, a)
    b = min(float(t_f), b)
    if a >= b:
        return 0.0

    params = TIMING_PARAMS[family]
    if family == SymptomFamily.SKIN:
        m_early, s_early = params[0]
        m_late, s_late = params[1]
        numerator = (
            SKIN_EARLY_WEIGHT * (_log_normal_cdf(b, m_early, s_early) - _log_normal_cdf(a, m_early, s_early))
            + (1 - SKIN_EARLY_WEIGHT) * (_log_normal_cdf(b, m_late, s_late) - _log_normal_cdf(a, m_late, s_late))
        )
        denominator = (
            SKIN_EARLY_WEIGHT * _log_normal_cdf(t_f, m_early, s_early)
            + (1 - SKIN_EARLY_WEIGHT) * _log_normal_cdf(t_f, m_late, s_late)
        )
    else:
        m, sigma = params[0]
        numerator = _log_normal_cdf(b, m, sigma) - _log_normal_cdf(a, m, sigma)
        denominator = _log_normal_cdf(t_f, m, sigma)

    if denominator == 0:
        return 0.0
    return numerator / denominator


def meal_strength(family: SymptomFamily, exposure: float) -> float:
    """Expected number of family reactions from one serving if the component is a real trigger.

    a_{c,f} = -ln(1 - s_f * e_c).
    """
    if not 0 <= exposure <= 1:
        raise ValueError(f"exposure must be between 0 and 1, got {exposure}")
    return -math.log(1 - REACTION_CHANCE[family] * exposure)


def symptom_evidence(
    pulls: dict[UUID, float],
    confidences: dict[UUID, float],
    background_rate: float,
) -> dict[UUID, float]:
    """Compute delta log-odds for each component after a symptom.

    S = lambda_f + sum(q_c * P_c), O_c = S - q_c * P_c, delta_l_c = ln(1 + P_c / O_c).
    """
    s_total = background_rate + sum(confidences.get(c, 0.0) * p for c, p in pulls.items())

    deltas: dict[UUID, float] = {}
    for c, p_c in pulls.items():
        q_c = confidences.get(c, 0.0)
        o_c = s_total - q_c * p_c
        if o_c <= 0 or p_c <= 0:
            deltas[c] = 0.0
        else:
            deltas[c] = math.log(1.0 + p_c / o_c)
    return deltas


def expected_reaction_penalty(
    strengths: dict[UUID, float],
    share: float,
) -> dict[UUID, float]:
    """Compute delta log-odds (negative) for each component from expected reactions.

    delta_l_c = -a_{c,f} * K_f(a, b).
    """
    return {c: -(a * share) for c, a in strengths.items()}
