"""Tests for the logging calendar: status rules, streaks, local-day grouping and the endpoints."""

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import event

from auth_context import current_username
from local_day import parse_timezone, to_local_date
from models.daily_health_metrics import DailyHealthMetrics
from models.food import Food
from models.food_log import FoodLog
from models.symptom import Symptom
from models.symptom_log import SymptomLog
from repositories.calendar_repository import CalendarRepository
from repositories.user_repository import UserRepository
from services.calendar_service import CalendarService, compute_streaks, day_status

NY = "America/New_York"


def at(day: str, hour: int = 12, minute: int = 0, tz: str = NY) -> datetime:
    """A timezone-aware instant at a local wall-clock time."""
    return datetime.combine(date.fromisoformat(day), datetime.min.time(), ZoneInfo(tz)).replace(
        hour=hour, minute=minute
    )


class Logs:
    """Adds logs for one user, acting as that user so the ownership filter stamps rows correctly."""

    def __init__(self, db, username: str):
        self.db = db
        self.username = username
        with self._as_user():
            self.food = Food(name="Rice", ingredients=["rice"], username=username)
            self.symptom = Symptom(name="Fatigue", location="General", sensation="Tired", username=username)
            db.add_all([self.food, self.symptom])
            db.flush()

    def _as_user(self):
        db, username = self.db, self.username

        class _Ctx:
            def __enter__(self):
                self.token = current_username.set(username)

            def __exit__(self, *exc):
                db.flush()
                current_username.reset(self.token)

        return _Ctx()

    def food_at(self, *instants: datetime) -> "Logs":
        with self._as_user():
            for ts in instants:
                self.db.add(FoodLog(username=self.username, food_id=self.food.id, timestamp=ts))
        return self

    def symptom_at(self, *instants: datetime) -> "Logs":
        with self._as_user():
            for ts in instants:
                self.db.add(SymptomLog(username=self.username, symptom_id=self.symptom.id, intensity=5, timestamp=ts))
        return self


@pytest.fixture
def logs(db_session, authenticated_user):
    return Logs(db_session, authenticated_user["username"])


@pytest.fixture
def other_user_logs(db_session, authenticated_user):
    """A second user's logs, on the same days as the signed-in user's."""
    UserRepository().create(db=db_session, username="someone_else", email="else@remetra.test")
    return Logs(db_session, "someone_else")


# ─── status rules ─────────────────────────────────────────────────────────────


class TestDayStatus:
    def test_needs_food_and_a_symptom_to_be_complete(self):
        assert day_status(2, 1) == "complete"

    def test_food_without_symptoms_is_food_only(self):
        # Symptom-free days count as food only until "No symptoms today" check-ins exist
        assert day_status(3, 0) == "food_only"

    def test_symptoms_without_food(self):
        assert day_status(0, 1) == "symptoms_only"

    def test_nothing_logged(self):
        assert day_status(0, 0) == "empty"


# ─── streaks ──────────────────────────────────────────────────────────────────


def days(*isos: str) -> set[date]:
    return {date.fromisoformat(d) for d in isos}


class TestStreaks:
    def test_current_streak_counts_back_from_today(self):
        assert compute_streaks(days("2026-10-10", "2026-10-11", "2026-10-12"), date(2026, 10, 12)) == (3, 3)

    def test_current_streak_starts_yesterday_when_today_is_not_logged_yet(self):
        assert compute_streaks(days("2026-10-10", "2026-10-11"), date(2026, 10, 12))[0] == 2

    def test_a_gap_before_yesterday_ends_the_current_streak(self):
        assert compute_streaks(days("2026-10-09"), date(2026, 10, 12))[0] == 0

    def test_streaks_cross_month_and_year_boundaries(self):
        assert compute_streaks(days("2026-12-30", "2026-12-31", "2027-01-01"), date(2027, 1, 1)) == (3, 3)

    def test_longest_streak_is_all_time(self):
        logged = days("2026-08-01", "2026-08-02", "2026-08-03", "2026-08-04", "2026-10-11", "2026-10-12")
        assert compute_streaks(logged, date(2026, 10, 12)) == (2, 4)

    def test_no_logs_means_no_streaks(self):
        assert compute_streaks(set(), date(2026, 10, 12)) == (0, 0)


# ─── local day ────────────────────────────────────────────────────────────────


class TestLocalDay:
    def test_parse_timezone_accepts_iana_names(self):
        assert parse_timezone(NY).key == NY

    @pytest.mark.parametrize("name", ["Not/AZone", "", "../etc/passwd", "America"])
    def test_parse_timezone_rejects_anything_else(self, name):
        with pytest.raises(ValueError):
            parse_timezone(name)

    def test_to_local_date_uses_the_local_clock(self):
        late = at("2026-10-12", 23, 30)  # 03:30 UTC on the 13th
        assert to_local_date(late, ZoneInfo(NY)) == date(2026, 10, 12)
        assert to_local_date(late, ZoneInfo("UTC")) == date(2026, 10, 13)


# ─── repository ───────────────────────────────────────────────────────────────


class TestCalendarRepository:
    def test_groups_by_local_day_in_the_requested_timezone(self, db_session, logs, authenticated_user):
        logs.food_at(at("2026-10-12", 23, 30))  # 23:30 in New York is already the 13th in Tokyo
        repo = CalendarRepository()
        start, end = date(2026, 10, 1), date(2026, 10, 31)

        ny = repo.get_food_counts(db_session, authenticated_user["username"], start, end, NY)
        tokyo_day = date(2026, 10, 13)
        tokyo = repo.get_food_counts(db_session, authenticated_user["username"], tokyo_day, tokyo_day, "Asia/Tokyo")

        assert ny == {date(2026, 10, 12): 1}
        assert tokyo == {date(2026, 10, 13): 1}

    def test_counts_food_and_symptoms_on_the_same_day(self, db_session, logs, authenticated_user):
        logs.food_at(at("2026-10-12", 8), at("2026-10-12", 19)).symptom_at(at("2026-10-12", 14))
        repo = CalendarRepository()
        start, end = date(2026, 10, 1), date(2026, 10, 31)

        food = repo.get_food_counts(db_session, authenticated_user["username"], start, end, NY)
        symptoms = repo.get_symptom_counts(db_session, authenticated_user["username"], start, end, NY)

        assert food == {date(2026, 10, 12): 2}
        assert symptoms == {date(2026, 10, 12): 1}

    def test_query_count_does_not_grow_with_history(self, db_session, logs, authenticated_user):
        service = CalendarService()

        def count_queries() -> int:
            queries = []
            listener = lambda *args: queries.append(1)  # noqa: E731
            event.listen(db_session.bind, "before_cursor_execute", listener)
            try:
                service.get_month(db_session, authenticated_user["username"], "2026-10", NY, today=date(2026, 10, 31))
            finally:
                event.remove(db_session.bind, "before_cursor_execute", listener)
            return len(queries)

        logs.food_at(*(at("2026-10-01") + timedelta(days=i) for i in range(30)))
        one_month = count_queries()
        logs.food_at(*(at("2024-10-01") + timedelta(days=i) for i in range(700)))
        two_years = count_queries()

        assert one_month == two_years == 4

    def test_health_dates_are_filtered_by_user_and_range(self, db_session, logs, other_user_logs, authenticated_user):
        username = authenticated_user["username"]
        db_session.add_all(
            [
                DailyHealthMetrics(username=username, date=date(2026, 10, 5), timezone=NY, sleep_total_min=420),
                DailyHealthMetrics(username=username, date=date(2026, 11, 1), timezone=NY, sleep_total_min=400),
                DailyHealthMetrics(username="someone_else", date=date(2026, 10, 6), timezone=NY, hrv_avg_ms=40),
            ]
        )
        db_session.flush()

        dates = CalendarRepository().get_health_dates(db_session, username, date(2026, 10, 1), date(2026, 10, 31))

        assert dates == {date(2026, 10, 5)}


# ─── service ──────────────────────────────────────────────────────────────────


class TestCalendarService:
    def test_month_has_one_entry_per_day_with_counts_and_status(self, db_session, logs, authenticated_user):
        logs.food_at(at("2026-10-12", 8)).symptom_at(at("2026-10-12", 9)).food_at(at("2026-10-13"))

        month = CalendarService().get_month(
            db_session, authenticated_user["username"], "2026-10", NY, date(2026, 10, 31)
        )

        assert month.month == "2026-10"
        assert len(month.days) == 31
        assert month.days[11].model_dump() == {
            "date": date(2026, 10, 12),
            "food_count": 1,
            "symptom_count": 1,
            "has_health_data": False,
            "status": "complete",
        }
        assert month.days[12].status == "food_only"
        assert month.days[0].status == "empty"

    def test_february_in_a_leap_year(self, db_session, logs, authenticated_user):
        month = CalendarService().get_month(db_session, authenticated_user["username"], "2028-02", NY, date(2028, 3, 1))

        assert len(month.days) == 29

    def test_streaks_use_history_outside_the_requested_month(self, db_session, logs, authenticated_user):
        logs.food_at(at("2026-09-29"), at("2026-09-30")).symptom_at(at("2026-10-01"))

        month = CalendarService().get_month(
            db_session, authenticated_user["username"], "2026-10", NY, date(2026, 10, 1)
        )

        assert (month.current_streak, month.longest_streak) == (3, 3)

    def test_marks_days_with_health_data(self, db_session, logs, authenticated_user):
        username = authenticated_user["username"]
        db_session.add(DailyHealthMetrics(username=username, date=date(2026, 10, 5), timezone=NY, hrv_avg_ms=45))
        db_session.flush()

        month = CalendarService().get_month(db_session, username, "2026-10", NY, date(2026, 10, 31))

        assert [d.date for d in month.days if d.has_health_data] == [date(2026, 10, 5)]

    def test_day_logs_are_that_local_day_in_time_order(self, db_session, logs, authenticated_user):
        logs.food_at(at("2026-10-12", 19), at("2026-10-12", 8), at("2026-10-13", 0, 15))
        logs.symptom_at(at("2026-10-12", 23, 30), at("2026-10-11", 23, 59))

        day = CalendarService().get_day_logs(db_session, authenticated_user["username"], date(2026, 10, 12), NY)

        assert [log.timestamp.astimezone(ZoneInfo(NY)).hour for log in day.food_logs] == [8, 19]
        assert len(day.symptom_logs) == 1

    def test_rejects_an_unknown_timezone(self, db_session, authenticated_user):
        with pytest.raises(ValueError):
            CalendarService().get_month(db_session, authenticated_user["username"], "2026-10", "Mars/Olympus")


# ─── endpoints ────────────────────────────────────────────────────────────────


class TestCalendarRouter:
    def test_month_requires_auth(self, test_client):
        assert test_client.get("/calendar/month", params={"month": "2026-10", "tz": NY}).status_code == 401

    def test_day_requires_auth(self, test_client):
        assert test_client.get("/calendar/day", params={"date": "2026-10-12", "tz": NY}).status_code == 401

    def test_month_returns_the_summary(self, test_client, logs):
        logs.food_at(at("2026-10-12")).symptom_at(at("2026-10-12"))

        response = test_client.get("/calendar/month", params={"month": "2026-10", "tz": NY})

        assert response.status_code == 200
        body = response.json()
        assert len(body["days"]) == 31
        assert body["days"][11] == {
            "date": "2026-10-12",
            "food_count": 1,
            "symptom_count": 1,
            "has_health_data": False,
            "status": "complete",
        }
        assert {"current_streak", "longest_streak"} <= body.keys()

    def test_day_returns_that_days_logs(self, test_client, logs):
        logs.food_at(at("2026-10-12", 23, 30)).symptom_at(at("2026-10-13", 0, 30))

        body = test_client.get("/calendar/day", params={"date": "2026-10-12", "tz": NY}).json()

        assert body["date"] == "2026-10-12"
        assert len(body["food_logs"]) == 1
        assert body["symptom_logs"] == []

    @pytest.mark.parametrize("month", ["2026-13", "2026-00", "2026-1", "26-10", "2026-10-01", "0000-01", "october"])
    def test_rejects_invalid_months(self, test_client, authenticated_user, month):
        assert test_client.get("/calendar/month", params={"month": month, "tz": NY}).status_code == 422

    @pytest.mark.parametrize("day", ["2026-02-30", "2026-13-01", "yesterday", ""])
    def test_rejects_invalid_dates(self, test_client, authenticated_user, day):
        assert test_client.get("/calendar/day", params={"date": day, "tz": NY}).status_code == 422

    @pytest.mark.parametrize("tz", ["Mars/Olympus", "", "America"])
    def test_rejects_invalid_timezones(self, test_client, authenticated_user, tz):
        assert test_client.get("/calendar/month", params={"month": "2026-10", "tz": tz}).status_code == 422
        assert test_client.get("/calendar/day", params={"date": "2026-10-12", "tz": tz}).status_code == 422

    def test_requires_month_and_timezone(self, test_client, authenticated_user):
        assert test_client.get("/calendar/month", params={"tz": NY}).status_code == 422
        assert test_client.get("/calendar/month", params={"month": "2026-10"}).status_code == 422

    def test_never_shows_another_users_logs(self, test_client, logs, other_user_logs):
        other_user_logs.food_at(at("2026-10-12")).symptom_at(at("2026-10-12"), at("2026-10-13"))
        logs.food_at(at("2026-10-12"))

        month = test_client.get("/calendar/month", params={"month": "2026-10", "tz": NY}).json()
        day = test_client.get("/calendar/day", params={"date": "2026-10-12", "tz": NY}).json()

        assert month["days"][11]["food_count"] == 1
        assert month["days"][11]["symptom_count"] == 0
        assert month["days"][12]["status"] == "empty"
        assert month["longest_streak"] == 1
        assert len(day["food_logs"]) == 1
        assert day["symptom_logs"] == []
