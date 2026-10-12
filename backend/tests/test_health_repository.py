from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from models.user import User
from repositories.health_repository import HealthRepository
from schemas.health import HealthDayEntry, HealthEventEntry


@pytest.fixture
def health_user(db_session):
    user = User(username="healthuser", email="health@test.com", password_hash="fakehash")
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def second_user(db_session):
    user = User(username="healthuser2", email="health2@test.com", password_hash="fakehash")
    db_session.add(user)
    db_session.flush()
    return user


def _day(**overrides):
    defaults = {
        "date": "2026-09-28",
        "sleep_total_min": 412,
        "sleep_deep_min": 58,
        "sleep_rem_min": 91,
        "sleep_core_min": 263,
        "sleep_awake_min": 24,
        "hrv_avg_ms": 40.4,
        "resting_hr_bpm": 61.0,
    }
    defaults.update(overrides)
    return HealthDayEntry(**defaults)


def _event(**overrides):
    defaults = {
        "hk_uuid": str(uuid4()),
        "category": "symptom",
        "type": "fatigue",
        "value": "moderate",
        "start_at": "2026-09-28T14:00:00Z",
        "end_at": "2026-09-28T18:00:00Z",
        "date": "2026-09-28",
    }
    defaults.update(overrides)
    return HealthEventEntry(**defaults)


class TestSaveDays:
    def test_inserts_new_day(self, db_session, health_user):
        repo = HealthRepository()
        result = repo.save_days(db_session, "healthuser", "America/New_York", [_day()])
        assert result == 1

    def test_upserts_existing_day(self, db_session, health_user):
        repo = HealthRepository()
        repo.save_days(db_session, "healthuser", "America/New_York", [_day(sleep_total_min=400)])
        result = repo.save_days(db_session, "healthuser", "America/New_York", [_day(sleep_total_min=500)])
        assert result == 1

    def test_returns_zero_for_empty_list(self, db_session, health_user):
        repo = HealthRepository()
        result = repo.save_days(db_session, "healthuser", "America/New_York", [])
        assert result == 0


class TestSaveEvents:
    def test_inserts_new_event(self, db_session, health_user):
        repo = HealthRepository()
        result = repo.save_events(db_session, "healthuser", [_event()])
        assert result == 1

    def test_skips_duplicate_hk_uuid(self, db_session, health_user):
        repo = HealthRepository()
        fixed_uuid = str(uuid4())
        repo.save_events(db_session, "healthuser", [_event(hk_uuid=fixed_uuid)])
        result = repo.save_events(db_session, "healthuser", [_event(hk_uuid=fixed_uuid)])
        assert result == 0

    def test_partial_skip_returns_correct_count(self, db_session, health_user):
        repo = HealthRepository()
        fixed_uuid = str(uuid4())
        repo.save_events(db_session, "healthuser", [_event(hk_uuid=fixed_uuid)])
        events = [_event(hk_uuid=fixed_uuid), _event(), _event()]
        result = repo.save_events(db_session, "healthuser", events)
        assert result == 2

    def test_returns_zero_for_empty_list(self, db_session, health_user):
        repo = HealthRepository()
        result = repo.save_events(db_session, "healthuser", [])
        assert result == 0

    def test_two_users_same_hk_uuid(self, db_session, health_user, second_user):
        repo = HealthRepository()
        shared_uuid = str(uuid4())
        result_a = repo.save_events(db_session, "healthuser", [_event(hk_uuid=shared_uuid)])
        result_b = repo.save_events(db_session, "healthuser2", [_event(hk_uuid=shared_uuid)])
        assert result_a == 1
        assert result_b == 1

    def test_rollback_on_db_error(self, db_session, health_user):
        repo = HealthRepository()
        with patch.object(db_session, "execute", side_effect=Exception("db error")):
            with pytest.raises(Exception, match="db error"):
                repo.save_events(db_session, "healthuser", [_event()])
