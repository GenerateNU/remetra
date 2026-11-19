"""Health days: repeatable, realistic, some missing, and a dip the day after a strong reaction."""

import random
from datetime import date, datetime, timedelta, timezone
from statistics import mean

from scripts.mock_users.health import build_health_days
from scripts.mock_users.meals import LOCAL_TZ
from scripts.mock_users.shapes import SymptomEvent, SymptomKind

END = date(2026, 11, 1)
KIND = SymptomKind("Bloating", "Abdomen")


def _event(day, intensity, planted):
    local = datetime(day.year, day.month, day.day, 18, tzinfo=LOCAL_TZ)
    return SymptomEvent(KIND, intensity, local.astimezone(timezone.utc), 60, planted)


def _days(seed, symptoms=(), days=40, missing_rate=0):
    return build_health_days(random.Random(seed), list(symptoms), END, days, missing_rate)


def test_same_seed_gives_same_days():
    symptoms = [_event(date(2026, 10, 10), 8, True)]

    assert _days(1, symptoms, missing_rate=0.1) == _days(1, symptoms, missing_rate=0.1)


def test_different_seeds_give_different_baselines():
    assert mean(d.hrv_avg_ms for d in _days(1)) != mean(d.hrv_avg_ms for d in _days(2))


def test_zero_days_gives_nothing():
    assert _days(1, days=0) == []


def test_covers_every_day_when_nothing_is_missing():
    days = _days(1, days=15)

    assert [d.date for d in days] == [END - timedelta(days=i) for i in range(14, -1, -1)]


def test_some_days_are_missing():
    assert 0 < len(_days(1, missing_rate=0.3)) < 40


def test_values_are_plausible_and_vary_day_to_day():
    days = _days(1)

    assert len({d.sleep_total_min for d in days}) > 1
    assert len({d.hrv_avg_ms for d in days}) > 1
    for d in days:
        assert d.sleep_deep_min + d.sleep_rem_min + d.sleep_core_min == d.sleep_total_min
        assert 300 <= d.sleep_total_min <= 600
        assert 15 <= d.hrv_avg_ms <= 90
        assert 45 <= d.resting_hr_bpm <= 75
        assert 10 <= d.sleep_awake_min <= 40


def test_sleep_and_hrv_dip_the_day_after_a_strong_reaction():
    strong = [date(2026, 10, d) for d in (3, 9, 15, 21, 27)]
    days = _days(1, [_event(d, 8, True) for d in strong])
    after = {d + timedelta(days=1) for d in strong}
    dipped = [d for d in days if d.date in after]
    normal = [d for d in days if d.date not in after]

    assert mean(d.sleep_total_min for d in dipped) < mean(d.sleep_total_min for d in normal) - 45
    assert mean(d.hrv_avg_ms for d in dipped) < mean(d.hrv_avg_ms for d in normal) - 7
    assert mean(d.resting_hr_bpm for d in dipped) > mean(d.resting_hr_bpm for d in normal) + 3


def test_mild_or_background_symptoms_do_not_dip():
    day = date(2026, 10, 15)
    symptoms = [_event(day, 6, True), _event(day, 9, False)]

    assert _days(1, symptoms) == _days(1)
