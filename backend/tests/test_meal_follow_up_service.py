"""Unit tests for MealFollowUpsService."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from models.food import Food
from models.food_log import FoodLog
from services.meal_follow_up_service import FOLLOW_UP_DELAY, MealFollowUpsService

LOGGED_AT = datetime(2025, 3, 1, 12, 0, tzinfo=timezone.utc)


def _food_log(timestamp: datetime = LOGGED_AT, food_name: str = "test pizza") -> FoodLog:
    log = FoodLog()
    log.id = uuid4()
    log.username = "alice"
    log.timestamp = timestamp
    food = Food()
    food.name = food_name
    log.food = food
    return log


@pytest.fixture
def service():
    """MealFollowUpsService with a mocked FoodLogRepository."""
    svc = MealFollowUpsService()
    svc.food_log_repo = MagicMock()
    return svc


class TestShouldSchedule:
    """Tests for MealFollowUpsService.should_schedule."""

    def test_returns_true_within_window(self, service):
        """A log newer than the follow up delay should be scheduled."""
        food_log = _food_log()
        service.food_log_repo.get_food_log_by_id.return_value = food_log
        now = LOGGED_AT + timedelta(minutes=30)

        result = service.should_schedule(MagicMock(), food_log.id, now=now)

        assert result is True

    def test_returns_false_at_window_boundary(self, service):
        """A log exactly FOLLOW_UP_DELAY old should not be scheduled."""
        food_log = _food_log()
        service.food_log_repo.get_food_log_by_id.return_value = food_log
        now = LOGGED_AT + FOLLOW_UP_DELAY

        result = service.should_schedule(MagicMock(), food_log.id, now=now)

        assert result is False

    def test_returns_false_outside_window(self, service):
        """A log older than the follow up delay should not be scheduled."""
        food_log = _food_log()
        service.food_log_repo.get_food_log_by_id.return_value = food_log
        now = LOGGED_AT + timedelta(hours=5)

        result = service.should_schedule(MagicMock(), food_log.id, now=now)

        assert result is False

    def test_defaults_now_to_current_time(self, service):
        """Without an explicit now, the current UTC time is used."""
        food_log = _food_log(timestamp=datetime.now(timezone.utc) - timedelta(minutes=10))
        service.food_log_repo.get_food_log_by_id.return_value = food_log

        result = service.should_schedule(MagicMock(), food_log.id)

        assert result is True

    def test_returns_none_when_log_missing(self, service):
        """A non-existent food log returns None."""
        service.food_log_repo.get_food_log_by_id.return_value = None

        result = service.should_schedule(MagicMock(), uuid4())

        assert result is None

    def test_passes_db_and_id_to_repository(self, service):
        """The repository is queried with the given session and food log ID."""
        db = MagicMock()
        food_log_id = uuid4()
        service.food_log_repo.get_food_log_by_id.return_value = None

        service.should_schedule(db, food_log_id)

        service.food_log_repo.get_food_log_by_id.assert_called_once_with(db, food_log_id)


class TestWhenToFire:
    """Tests for MealFollowUpsService.when_to_fire."""

    def test_returns_timestamp_plus_delay(self, service):
        """Fire time is the log timestamp plus FOLLOW_UP_DELAY."""
        food_log = _food_log()
        service.food_log_repo.get_food_log_by_id.return_value = food_log

        result = service.when_to_fire(MagicMock(), food_log.id)

        assert result == LOGGED_AT + FOLLOW_UP_DELAY

    def test_returns_none_when_log_missing(self, service):
        """A non-existent food log returns None."""
        service.food_log_repo.get_food_log_by_id.return_value = None

        result = service.when_to_fire(MagicMock(), uuid4())

        assert result is None


class TestBuildMessage:
    """Tests for MealFollowUpsService.build_message."""

    def test_includes_food_name(self, service):
        """The message references the logged food by name."""
        food_log = _food_log(food_name="ramen")
        service.food_log_repo.get_food_log_by_id.return_value = food_log

        result = service.build_message(MagicMock(), food_log.id)

        assert result == "It's been a couple hours since your ramen. Any symptoms to log?"

    def test_returns_none_when_log_missing(self, service):
        """A non-existent food log returns None."""
        service.food_log_repo.get_food_log_by_id.return_value = None

        result = service.build_message(MagicMock(), uuid4())

        assert result is None
