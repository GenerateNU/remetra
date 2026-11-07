"""Router tests for GET /health/trends"""

from datetime import UTC, date, datetime

import pytest

from models.symptom import Symptom
from models.symptom_log import SymptomLog
from repositories.health_repository import HealthRepository
from schemas.health import HealthDayEntry


@pytest.fixture
def created_symptom(db_session, authenticated_user, sample_symptom_data):
    """A real symptom row so symptom logs can reference it."""
    symptom = Symptom(**sample_symptom_data)
    db_session.add(symptom)
    db_session.commit()
    db_session.refresh(symptom)
    return symptom


def _seed_health_day(db_session, username, day):
    HealthRepository().save_days(
        db_session,
        username,
        "America/New_York",
        [HealthDayEntry(date=day, sleep_total_min=420, hrv_avg_ms=50.0, resting_hr_bpm=60.0)],
    )


def _seed_symptom_log(db_session, username, symptom_id, timestamp, intensity):
    db_session.add(
        SymptomLog(username=username, symptom_id=symptom_id, intensity=intensity, timestamp=timestamp)
    )
    db_session.commit()


class TestHealthTrendsRouter:
    """HTTP tests for the health trends endpoint."""

    def test_returns_one_entry_per_day(self, test_client, authenticated_user, db_session, created_symptom):
        """Each day in range gets an entry, with null metrics and symptom counts filled in correctly"""
        username = authenticated_user["username"]
        _seed_health_day(db_session, username, date(2026, 10, 20))
        _seed_symptom_log(db_session, username, created_symptom.id, datetime(2026, 10, 21, 14, 0, tzinfo=UTC), 3)
        _seed_symptom_log(db_session, username, created_symptom.id, datetime(2026, 10, 21, 18, 0, tzinfo=UTC), 6)

        response = test_client.get("/health/trends", params={"start": "2026-10-20", "end": "2026-10-22"})

        assert response.status_code == 200
        days = response.json()
        assert [d["date"] for d in days] == ["2026-10-20", "2026-10-21", "2026-10-22"]

        assert days[0]["sleep_total_min"] == 420
        assert days[0]["symptom_count"] == 0
        assert days[0]["max_intensity"] is None

        assert days[1]["sleep_total_min"] is None
        assert days[1]["hrv_avg_ms"] is None
        assert days[1]["resting_hr_bpm"] is None
        assert days[1]["symptom_count"] == 2
        assert days[1]["max_intensity"] == 6

        assert days[2]["sleep_total_min"] is None
        assert days[2]["symptom_count"] == 0

    def test_ninety_day_range(self, test_client, authenticated_user):
        """Exactly 90 days (inclusive) is the maximum allowed range."""
        response = test_client.get("/health/trends", params={"start": "2026-08-01", "end": "2026-10-29"})

        assert response.status_code == 200
        assert len(response.json()) == 90

    def test_range_over_ninety_days_422(self, test_client, authenticated_user):
        """A range exceeding 90 days will be rejected"""
        response = test_client.get("/health/trends", params={"start": "2026-08-01", "end": "2026-10-30"})

        assert response.status_code == 422

    def test_end_before_start_422(self, test_client, authenticated_user):
        """An end date before the start date is rejected"""
        response = test_client.get("/health/trends", params={"start": "2026-10-22", "end": "2026-10-20"})

        assert response.status_code == 422

    def test_missing_token_401(self, test_client):
        """A request without a valid token is rejected"""
        response = test_client.get("/health/trends", params={"start": "2026-10-20", "end": "2026-10-22"})

        assert response.status_code == 401