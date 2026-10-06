"""Integration tests for the meal follow up router."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from schemas.food_log import FoodLogCreate
from schemas.user import UserCreate
from services.auth_service import AuthService
from services.food_log_service import FoodLogService
from services.meal_follow_up_service import FOLLOW_UP_DELAY


def _create_food_log(db_session, username, food_id, timestamp):
    return FoodLogService().create_food_log(
        db_session,
        FoodLogCreate(username=username, food_id=food_id, timestamp=timestamp),
    )


@pytest.fixture
def auth_headers(authenticated_user):
    """Bearer auth header for the authenticated test user."""
    return {"Authorization": f"Bearer {authenticated_user['token']}"}


@pytest.fixture
def recent_food_log(db_session, authenticated_user, created_food):
    """A food log from 30 minutes ago — inside the follow up window."""
    timestamp = datetime.now(timezone.utc) - timedelta(minutes=30)
    return _create_food_log(db_session, authenticated_user["username"], created_food.id, timestamp)


@pytest.fixture
def old_food_log(db_session, authenticated_user, created_food):
    """A food log from 5 hours ago — outside the follow up window."""
    timestamp = datetime.now(timezone.utc) - timedelta(hours=5)
    return _create_food_log(db_session, authenticated_user["username"], created_food.id, timestamp)


class TestGetMealFollowUp:
    """Tests for GET /meal-follow-ups/{food_log_id}."""

    def test_recent_log_returns_scheduled_follow_up(self, test_client, auth_headers, recent_food_log, created_food):
        """A recent log returns a follow up that should be scheduled."""
        response = test_client.get(f"/meal-follow-ups/{recent_food_log.id}", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["should_schedule"] is True
        assert datetime.fromisoformat(body["fire_at"]) == recent_food_log.timestamp + FOLLOW_UP_DELAY
        assert body["title"] == "How are you feeling?"
        assert body["body"] == f"It's been a couple hours since your {created_food.name}. Any symptoms to log?"
        assert body["data"] == {"log_type": "symptom", "food_log_id": str(recent_food_log.id)}

    def test_old_log_should_not_be_scheduled(self, test_client, auth_headers, old_food_log):
        """A log older than the follow up window returns should_schedule False."""
        response = test_client.get(f"/meal-follow-ups/{old_food_log.id}", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["should_schedule"] is False
        assert datetime.fromisoformat(body["fire_at"]) == old_food_log.timestamp + FOLLOW_UP_DELAY

    def test_missing_log_returns_404(self, test_client, auth_headers):
        """A non-existent food log ID returns 404."""
        missing_id = uuid4()

        response = test_client.get(f"/meal-follow-ups/{missing_id}", headers=auth_headers)

        assert response.status_code == 404
        assert response.json()["detail"] == f"Food log with ID {missing_id} not found"

    def test_other_users_log_returns_404(self, test_client, db_session, recent_food_log):
        """A user cannot fetch the follow up for another user's food log."""
        auth_service = AuthService()
        auth_service.register_user(
            db_session, UserCreate(username="otheruser", email="other@example.com", password="password123")
        )
        token = auth_service.authenticate_user(db_session, "otheruser", "password123")["access_token"]

        response = test_client.get(
            f"/meal-follow-ups/{recent_food_log.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404

    def test_unauthenticated_request_returns_401(self, test_client, recent_food_log):
        """Requests without a bearer token are rejected."""
        response = test_client.get(f"/meal-follow-ups/{recent_food_log.id}")

        assert response.status_code == 401

    def test_invalid_uuid_returns_422(self, test_client, auth_headers):
        """A malformed food log ID fails path validation."""
        response = test_client.get("/meal-follow-ups/not-a-uuid", headers=auth_headers)

        assert response.status_code == 422
