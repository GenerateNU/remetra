import pytest
from pydantic import ValidationError

from schemas.health import HealthDayEntry, HealthEventEntry, HealthSyncRequest

VALID_DAY = {
    "date": "2026-09-28",
    "sleep_total_min": 412,
    "sleep_deep_min": 58,
    "sleep_rem_min": 91,
    "sleep_core_min": 263,
    "sleep_awake_min": 24,
    "hrv_avg_ms": 40.4,
    "resting_hr_bpm": 61,
}

VALID_EVENT = {
    "hk_uuid": "8F2A1C3E-4B5D-4E6F-9A0B-1C2D3E4F5A6B",
    "category": "symptom",
    "type": "fatigue",
    "value": "moderate",
    "start_at": "2026-09-28T14:00:00Z",
    "end_at": "2026-09-28T18:00:00Z",
    "date": "2026-09-28",
}


class TestHealthSyncRequest:
    def test_example_request_body_accepted(self):
        request = HealthSyncRequest(
            timezone="America/New_York",
            days=[VALID_DAY],
            events=[VALID_EVENT],
        )
        assert len(request.days) == 1
        assert len(request.events) == 1
        assert request.timezone == "America/New_York"


class TestHealthDayEntry:
    def test_all_fields(self):
        day = HealthDayEntry(**VALID_DAY)
        assert day.sleep_total_min == 412
        assert day.hrv_avg_ms == 40.4

    def test_partial_fields_accepted(self):
        day = HealthDayEntry(date="2026-09-28", sleep_total_min=400)
        assert day.sleep_total_min == 400
        assert day.sleep_deep_min is None
        assert day.hrv_avg_ms is None

    def test_only_date_accepted(self):
        day = HealthDayEntry(date="2026-09-28")
        assert day.sleep_total_min is None

    def test_negative_sleep_minutes_rejected(self):
        with pytest.raises(ValidationError):
            HealthDayEntry(**{**VALID_DAY, "sleep_total_min": -1})

    def test_sleep_minutes_over_1440_rejected(self):
        with pytest.raises(ValidationError):
            HealthDayEntry(**{**VALID_DAY, "sleep_total_min": 1441})

    def test_malformed_date_rejected(self):
        with pytest.raises(ValidationError):
            HealthDayEntry(**{**VALID_DAY, "date": "not-a-date"})


class TestHealthEventEntry:
    def test_valid_symptom_event(self):
        event = HealthEventEntry(**VALID_EVENT)
        assert event.category == "symptom"
        assert event.value == "moderate"

    def test_valid_menstrual_flow_event(self):
        event = HealthEventEntry(**{**VALID_EVENT, "category": "menstrual_flow", "value": "heavy"})
        assert event.category == "menstrual_flow"
        assert event.value == "heavy"

    def test_unknown_category_rejected(self):
        with pytest.raises(ValidationError):
            HealthEventEntry(**{**VALID_EVENT, "category": "banana"})

    def test_symptom_with_flow_value_rejected(self):
        with pytest.raises(ValidationError):
            HealthEventEntry(**{**VALID_EVENT, "category": "symptom", "value": "heavy"})

    def test_flow_with_symptom_value_rejected(self):
        with pytest.raises(ValidationError):
            HealthEventEntry(**{**VALID_EVENT, "category": "menstrual_flow", "value": "moderate"})

    def test_malformed_date_rejected(self):
        with pytest.raises(ValidationError):
            HealthEventEntry(**{**VALID_EVENT, "date": "not-a-date"})
