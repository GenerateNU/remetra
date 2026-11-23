"""Builds a user's daily Apple Health rows around their own baseline, with a dip the day after a strong reaction."""

import random
from datetime import date, timedelta

from schemas.health import HealthDayEntry
from scripts.mock_users.meals import LOCAL_TZ
from scripts.mock_users.shapes import SymptomEvent

TIMEZONE = LOCAL_TZ.key
DEFAULT_MISSING_RATE = 0.08
STRONG_INTENSITY = 7  # planted reactions at or above this dip the next day

# Each user's baseline is drawn once from the range, then each day adds noise.
SLEEP_BASELINE_MIN = (400, 480)
SLEEP_NOISE_MIN = 20
SLEEP_DIP_MIN = (60, 100)
HRV_BASELINE_MS = (35.0, 70.0)
HRV_NOISE_MS = 4.0
HRV_DIP_MS = (10.0, 16.0)
RHR_BASELINE_BPM = (52.0, 66.0)
RHR_NOISE_BPM = 1.5
RHR_RISE_BPM = (4.0, 7.0)


def _strong_reaction_days(symptoms: list[SymptomEvent]) -> set[date]:
    return {s.timestamp.astimezone(LOCAL_TZ).date() for s in symptoms if s.planted and s.intensity >= STRONG_INTENSITY}


def _sleep_stages(rng: random.Random, total: int) -> tuple[int, int, int]:
    """Deep, REM and core minutes that add up to total sleep."""
    deep = int(total * rng.uniform(0.13, 0.23))
    rem = int(total * rng.uniform(0.18, 0.25))
    return deep, rem, total - deep - rem


def build_health_days(
    rng: random.Random,
    symptoms: list[SymptomEvent],
    end_date: date,
    days: int,
    missing_rate: float = DEFAULT_MISSING_RATE,
) -> list[HealthDayEntry]:
    """`days` days of health metrics ending on `end_date`. Missing days are left out."""
    sleep_base = rng.randint(*SLEEP_BASELINE_MIN)
    hrv_base = rng.uniform(*HRV_BASELINE_MS)
    rhr_base = rng.uniform(*RHR_BASELINE_BPM)
    strong = _strong_reaction_days(symptoms)
    entries = []
    for offset in range(days - 1, -1, -1):
        day = end_date - timedelta(days=offset)
        if rng.random() < missing_rate:
            continue
        sleep = sleep_base + round(rng.gauss(0, SLEEP_NOISE_MIN))
        hrv = hrv_base + rng.gauss(0, HRV_NOISE_MS)
        rhr = rhr_base + rng.gauss(0, RHR_NOISE_BPM)
        if day - timedelta(days=1) in strong:
            sleep -= rng.randint(*SLEEP_DIP_MIN)
            hrv -= rng.uniform(*HRV_DIP_MS)
            rhr += rng.uniform(*RHR_RISE_BPM)
        deep, rem, core = _sleep_stages(rng, sleep)
        entries.append(
            HealthDayEntry(
                date=day,
                sleep_total_min=sleep,
                sleep_deep_min=deep,
                sleep_rem_min=rem,
                sleep_core_min=core,
                sleep_awake_min=rng.randint(10, 40),
                hrv_avg_ms=round(hrv, 1),
                resting_hr_bpm=round(rhr, 1),
            )
        )
    return entries
