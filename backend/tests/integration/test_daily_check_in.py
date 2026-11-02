"""Integration tests for daily check-ins."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from repositories.daily_check_in_repository import DailyCheckInRepository
from schemas.daily_check_in import DailyCheckInCreate

TIMEZONE = "America/New_York"


def _today():
    return datetime.now(ZoneInfo(TIMEZONE)).date()


def _check_in(test_client, day, timezone=TIMEZONE):
    return test_client.post("/check-ins/no-symptoms", json={"date": day.isoformat(), "timezone": timezone})


class TestDailyCheckInRouter:
    """HTTP tests for the no-symptoms check-in endpoint."""

    def test_creates_check_in(self, test_client, authenticated_user):
        """A valid check-in is saved for the signed-in user."""
        response = _check_in(test_client, _today())

        assert response.status_code == 200, response.text
        assert response.json()["date"] == _today().isoformat()
        assert response.json()["timezone"] == TIMEZONE
        assert response.json()["username"] == authenticated_user["username"]

    def test_repeating_returns_same_check_in(self, test_client, authenticated_user):
        """Checking in twice for the same date returns the same row."""
        first = _check_in(test_client, _today())
        second = _check_in(test_client, _today())

        assert second.status_code == 200
        assert second.json()["id"] == first.json()["id"]

    def test_seven_days_ago_is_allowed(self, test_client, authenticated_user):
        """The oldest allowed check-in is exactly 7 days ago"""
        response = _check_in(test_client, _today() - timedelta(days=7))

        assert response.status_code == 200

    def test_more_than_seven_days_ago_returns_422(self, test_client, authenticated_user):
        """A check-in older than 7 days is rejected."""
        response = _check_in(test_client, _today() - timedelta(days=8))

        assert response.status_code == 422

    def test_future_date_returns_422(self, test_client, authenticated_user):
        """A check-in for tomorrow is rejected."""
        response = _check_in(test_client, _today() + timedelta(days=1))

        assert response.status_code == 422

    def test_invalid_timezone_returns_422(self, test_client, authenticated_user):
        """A timezone that doesn't exist is rejected."""
        response = _check_in(test_client, _today(), timezone="Mars/Olympus")

        assert response.status_code == 422



class TestDailyCheckInRepository:
    """Integration tests for DailyCheckInRepository."""

    def test_get_check_in_dates_returns_dates_in_range(self, db_session, authenticated_user):
        """Returns check-in dates within the range, including both ends."""
        repo = DailyCheckInRepository()
        username = authenticated_user["username"]
        today = _today()
        for days_ago in (1, 3, 5):
            check_in = DailyCheckInCreate(date=today - timedelta(days=days_ago), timezone=TIMEZONE)
            repo.create(db_session, username, check_in)

        result = repo.get_check_in_dates(db_session, username, today - timedelta(days=3), today - timedelta(days=1))

        assert result == {today - timedelta(days=1), today - timedelta(days=3)}
