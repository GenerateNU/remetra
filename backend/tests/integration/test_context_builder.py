"""Integration tests for the chatbot ContextBuilder against a real database.

"Now" is frozen inside chatbot.context_builder so window boundaries are exact.
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from auth_context import current_username
from chatbot.context_builder import FOOD_LOG_FIELDS, SYMPTOM_LOG_FIELDS, ContextBuilder
from repositories.symptom_repository import SymptomRepository
from repositories.user_repository import UserRepository
from schemas.food_log import FoodLogCreate
from schemas.symptom import SymptomCreate
from schemas.symptom_log import SymptomLogCreate
from services.food_log_service import FoodLogService
from services.symptom_log_service import SymptomLogService

FROZEN_NOW = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
ONE_MICROSECOND = timedelta(microseconds=1)


class _FrozenDatetime(datetime):
    """datetime whose now() always returns FROZEN_NOW."""

    @classmethod
    def now(cls, tz=None):
        return FROZEN_NOW.astimezone(tz) if tz else FROZEN_NOW.replace(tzinfo=None)


# --------------------------------------------------------------------------- #
# Fixtures and helpers
# --------------------------------------------------------------------------- #


@pytest.fixture(autouse=True)
def frozen_now(monkeypatch):
    monkeypatch.setattr("chatbot.context_builder.datetime", _FrozenDatetime)
    return FROZEN_NOW


@pytest.fixture
def builder():
    return ContextBuilder()


@pytest.fixture
def symptom(db_session, authenticated_user):
    return SymptomRepository().create_symptom(
        db_session, SymptomCreate(name="headache", location="head", sensation="ache")
    )


@pytest.fixture
def second_symptom(db_session, authenticated_user):
    return SymptomRepository().create_symptom(
        db_session, SymptomCreate(name="bloating", location="stomach", sensation="pressure")
    )


@pytest.fixture
def other_user(db_session, authenticated_user):
    """A second user. Rows created inside `as_other_user()` are owned by them."""
    UserRepository().create(
        db=db_session, username="otheruser", email="other@example.com", clerk_user_id="user_otherclerk"
    )
    return "otheruser"


class _AsUser:
    """Temporarily switch the signed-in user so new rows are stamped with them."""

    def __init__(self, username):
        self.username = username

    def __enter__(self):
        self.token = current_username.set(self.username)

    def __exit__(self, *exc):
        current_username.reset(self.token)


def log_food(db, food_id, timestamp):
    return FoodLogService().create_food_log(db, FoodLogCreate(food_id=food_id, timestamp=timestamp))


def log_symptom(db, symptom_id, timestamp, intensity=5):
    return SymptomLogService().create_symptom_log(
        db, SymptomLogCreate(symptom_id=symptom_id, intensity=intensity, timestamp=timestamp)
    )


def ids(logs):
    """Identify logs by timestamp, since the bot-facing dicts carry no log id."""
    return {log["timestamp"] for log in logs}


HIDDEN_FIELDS = {"id", "username", "created_at"}


# --------------------------------------------------------------------------- #
# get_logs
# --------------------------------------------------------------------------- #


class TestGetLogs:
    def test_returns_empty_structure_when_user_has_no_logs(self, db_session, builder, authenticated_user):
        result = builder.get_logs(db_session)

        assert result == {"food_logs": [], "symptom_logs": [], "check_ins": []}

    def test_returns_logs_inside_window(self, db_session, builder, created_food, symptom):
        food = log_food(db_session, created_food.id, FROZEN_NOW - timedelta(days=5))
        sym = log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=5))

        result = builder.get_logs(db_session)

        assert ids(result["food_logs"]) == {food.timestamp}
        assert ids(result["symptom_logs"]) == {sym.timestamp}

    def test_returns_only_bot_facing_fields(self, db_session, builder, created_food, symptom):
        log_food(db_session, created_food.id, FROZEN_NOW - timedelta(days=1))
        log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=1))

        result = builder.get_logs(db_session)

        assert [set(log) for log in result["food_logs"]] == [FOOD_LOG_FIELDS]
        assert [set(log) for log in result["symptom_logs"]] == [SYMPTOM_LOG_FIELDS]

    def test_hides_id_username_and_created_at(self, db_session, builder, created_food, symptom):
        log_food(db_session, created_food.id, FROZEN_NOW - timedelta(days=1))
        log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=1))

        result = builder.get_logs(db_session)

        logs = result["food_logs"] + result["symptom_logs"]
        assert len(logs) == 2
        for log in logs:
            assert "id" not in log
            assert "username" not in log
            assert "created_at" not in log
            assert "testuser" not in log.values()

    def test_returns_plain_dicts(self, db_session, builder, created_food, symptom):
        log_food(db_session, created_food.id, FROZEN_NOW - timedelta(days=1))
        log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=1))

        result = builder.get_logs(db_session)

        assert all(type(log) is dict for log in result["food_logs"] + result["symptom_logs"])

    def test_field_values_match_logged_entry(self, db_session, builder, created_food, symptom):
        when = FROZEN_NOW - timedelta(days=1)
        log_symptom(db_session, symptom.id, when, intensity=7)

        (log,) = builder.get_logs(db_session)["symptom_logs"]

        assert log["symptom_id"] == symptom.id
        assert log["intensity"] == 7
        assert log["timestamp"] == when

    def test_excludes_logs_older_than_window(self, db_session, builder, created_food, symptom):
        log_food(db_session, created_food.id, FROZEN_NOW - timedelta(days=60))
        log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=60))

        result = builder.get_logs(db_session)

        assert result["food_logs"] == []
        assert result["symptom_logs"] == []

    def test_excludes_future_logs(self, db_session, builder, created_food, symptom):
        log_food(db_session, created_food.id, FROZEN_NOW + ONE_MICROSECOND)
        log_symptom(db_session, symptom.id, FROZEN_NOW + timedelta(days=1))

        result = builder.get_logs(db_session)

        assert result["food_logs"] == []
        assert result["symptom_logs"] == []

    def test_includes_log_exactly_at_now(self, db_session, builder, created_food, symptom):
        food = log_food(db_session, created_food.id, FROZEN_NOW)
        sym = log_symptom(db_session, symptom.id, FROZEN_NOW)

        result = builder.get_logs(db_session)

        assert ids(result["food_logs"]) == {food.timestamp}
        assert ids(result["symptom_logs"]) == {sym.timestamp}

    def test_default_window_includes_log_exactly_30_days_ago(self, db_session, builder, created_food, symptom):
        food = log_food(db_session, created_food.id, FROZEN_NOW - timedelta(days=30))
        sym = log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=30))

        result = builder.get_logs(db_session)

        assert ids(result["food_logs"]) == {food.timestamp}
        assert ids(result["symptom_logs"]) == {sym.timestamp}

    def test_default_window_excludes_log_just_over_30_days_ago(self, db_session, builder, created_food, symptom):
        log_food(db_session, created_food.id, FROZEN_NOW - timedelta(days=30) - ONE_MICROSECOND)
        log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=30) - ONE_MICROSECOND)

        result = builder.get_logs(db_session)

        assert result["food_logs"] == []
        assert result["symptom_logs"] == []

    def test_custom_days_narrows_window(self, db_session, builder, created_food, symptom):
        recent = log_food(db_session, created_food.id, FROZEN_NOW - timedelta(days=6))
        log_food(db_session, created_food.id, FROZEN_NOW - timedelta(days=8))
        recent_sym = log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=7))
        log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=7) - ONE_MICROSECOND)

        result = builder.get_logs(db_session, days=7)

        assert ids(result["food_logs"]) == {recent.timestamp}
        assert ids(result["symptom_logs"]) == {recent_sym.timestamp}

    def test_mixed_logs_only_returns_those_in_window(self, db_session, builder, created_food, symptom):
        inside = {
            log_food(db_session, created_food.id, FROZEN_NOW - timedelta(days=d)).timestamp for d in (0, 1, 15, 29)
        }
        for d in (31, 90, -1):
            log_food(db_session, created_food.id, FROZEN_NOW - timedelta(days=d))

        result = builder.get_logs(db_session)

        assert ids(result["food_logs"]) == inside

    def test_days_zero_only_includes_logs_at_exactly_now(self, db_session, builder, created_food, symptom):
        at_now = log_food(db_session, created_food.id, FROZEN_NOW)
        log_food(db_session, created_food.id, FROZEN_NOW - ONE_MICROSECOND)

        result = builder.get_logs(db_session, days=0)

        assert ids(result["food_logs"]) == {at_now.timestamp}

    def test_negative_days_returns_no_logs(self, db_session, builder, created_food, symptom):
        log_food(db_session, created_food.id, FROZEN_NOW)
        log_food(db_session, created_food.id, FROZEN_NOW + timedelta(days=2))
        log_symptom(db_session, symptom.id, FROZEN_NOW + timedelta(days=2))

        result = builder.get_logs(db_session, days=-5)

        assert result["food_logs"] == []
        assert result["symptom_logs"] == []

    def test_compares_non_utc_timestamps_by_instant_not_wall_clock(self, db_session, builder, created_food):
        plus_five = timezone(timedelta(hours=5))
        # 30 days + 1 hour ago in UTC. In +05:00 the wall clock reads 4 hours *after*
        # the window start, so a naive comparison would wrongly include it.
        outside = (FROZEN_NOW - timedelta(days=30, hours=1)).astimezone(plus_five)
        # 1 hour ago in UTC. In +05:00 the wall clock reads 4 hours in the *future*,
        # so a naive comparison would wrongly exclude it.
        inside = (FROZEN_NOW - timedelta(hours=1)).astimezone(plus_five)
        log_food(db_session, created_food.id, outside)
        expected = log_food(db_session, created_food.id, inside)

        result = builder.get_logs(db_session)

        assert ids(result["food_logs"]) == {expected.timestamp}

    # --- ownership ------------------------------------------------------------

    def test_requires_signed_in_user(self, db_session, builder, symptom):
        log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=1))
        token = current_username.set(None)
        try:
            with pytest.raises(ValueError, match="Authenticated username is required"):
                builder.get_logs(db_session)
        finally:
            current_username.reset(token)

    def test_excludes_other_users_logs(self, db_session, builder, symptom, other_user):
        mine = log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=1))
        with _AsUser(other_user):
            their_symptom = SymptomRepository().create_symptom(
                db_session, SymptomCreate(name="rash", location="arm", sensation="itch")
            )
            log_symptom(db_session, their_symptom.id, FROZEN_NOW - timedelta(days=2))

        result = builder.get_logs(db_session)

        assert ids(result["symptom_logs"]) == {mine.timestamp}

    def test_other_user_sees_only_their_own_logs(self, db_session, builder, symptom, other_user):
        log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=1))
        with _AsUser(other_user):
            their_symptom = SymptomRepository().create_symptom(
                db_session, SymptomCreate(name="rash", location="arm", sensation="itch")
            )
            theirs = log_symptom(db_session, their_symptom.id, FROZEN_NOW - timedelta(days=2))

            result = builder.get_logs(db_session)

        assert ids(result["symptom_logs"]) == {theirs.timestamp}

    def test_cannot_read_another_users_logs(self, db_session, builder, symptom, other_user):
        with _AsUser(other_user):
            their_symptom = SymptomRepository().create_symptom(
                db_session, SymptomCreate(name="rash", location="arm", sensation="itch")
            )
            log_symptom(db_session, their_symptom.id, FROZEN_NOW - timedelta(days=1))

        # Still signed in as testuser, who has no logs; otheruser's must not leak.
        result = builder.get_logs(db_session)

        assert result == {"food_logs": [], "symptom_logs": [], "check_ins": []}

    def test_unknown_user_sees_nothing(self, db_session, builder, symptom):
        log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=1))

        with _AsUser("nobody"):
            result = builder.get_logs(db_session)

        assert result == {"food_logs": [], "symptom_logs": [], "check_ins": []}


# --------------------------------------------------------------------------- #
# get_trends
# --------------------------------------------------------------------------- #


class TestGetTrends:
    def test_returns_empty_dict_when_no_symptom_logs(self, db_session, builder, authenticated_user):
        assert builder.get_trends(db_session) == {}

    def test_ignores_food_logs(self, db_session, builder, created_food):
        log_food(db_session, created_food.id, FROZEN_NOW - timedelta(days=1))

        assert builder.get_trends(db_session) == {}

    def test_single_log_summary(self, db_session, builder, symptom):
        log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=1), intensity=4)

        result = builder.get_trends(db_session)

        assert result == {
            "headache": {
                "count": 1,
                "avg_intensity": 4.0,
                "max_intensity": 4,
                "min_intensity": 4,
                "avg_logs_per_day": 0.0,  # round(1 / 30, 1)
            }
        }

    def test_keys_are_symptom_names_not_ids(self, db_session, builder, symptom):
        log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=1))

        result = builder.get_trends(db_session)

        assert set(result) == {"headache"}
        assert str(symptom.id) not in result
        assert all(HIDDEN_FIELDS.isdisjoint(stats) for stats in result.values())

    def test_multiple_logs_for_one_symptom(self, db_session, builder, symptom):
        for intensity in (2, 5, 9):
            log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=1), intensity=intensity)

        stats = builder.get_trends(db_session)["headache"]

        assert stats["count"] == 3
        assert stats["avg_intensity"] == 5.3  # 16 / 3 = 5.333...
        assert stats["max_intensity"] == 9
        assert stats["min_intensity"] == 2
        assert stats["avg_logs_per_day"] == 0.1  # 3 / 30

    def test_avg_intensity_rounds_to_one_decimal(self, db_session, builder, symptom):
        for intensity in (1, 2, 2):
            log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=1), intensity=intensity)

        stats = builder.get_trends(db_session)["headache"]

        assert stats["avg_intensity"] == 1.7  # 5 / 3 = 1.666...

    def test_handles_intensity_bounds(self, db_session, builder, symptom):
        log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=1), intensity=1)
        log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=1), intensity=10)

        stats = builder.get_trends(db_session)["headache"]

        assert stats["min_intensity"] == 1
        assert stats["max_intensity"] == 10
        assert stats["avg_intensity"] == 5.5

    def test_groups_by_symptom_name(self, db_session, builder, symptom, second_symptom):
        log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=1), intensity=3)
        log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=2), intensity=7)
        log_symptom(db_session, second_symptom.id, FROZEN_NOW - timedelta(days=1), intensity=8)

        result = builder.get_trends(db_session)

        assert set(result) == {"headache", "bloating"}
        assert result["headache"]["count"] == 2
        assert result["headache"]["avg_intensity"] == 5.0
        assert result["bloating"]["count"] == 1
        assert result["bloating"]["avg_intensity"] == 8.0

    def test_only_counts_logs_inside_window(self, db_session, builder, symptom):
        log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=1), intensity=2)
        log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=45), intensity=10)
        log_symptom(db_session, symptom.id, FROZEN_NOW + timedelta(days=1), intensity=10)

        stats = builder.get_trends(db_session)["headache"]

        assert stats["count"] == 1
        assert stats["max_intensity"] == 2

    def test_symptom_with_only_out_of_window_logs_is_absent(self, db_session, builder, symptom, second_symptom):
        log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=1))
        log_symptom(db_session, second_symptom.id, FROZEN_NOW - timedelta(days=45))

        result = builder.get_trends(db_session)

        assert set(result) == {"headache"}

    @pytest.mark.parametrize(
        ("days", "num_logs", "expected_frequency"),
        [
            (7, 7, 1.0),
            (2, 3, 1.5),
            (10, 1, 0.1),
            (1, 4, 4.0),
        ],
    )
    def test_avg_logs_per_day(self, db_session, builder, symptom, days, num_logs, expected_frequency):
        for _ in range(num_logs):
            log_symptom(db_session, symptom.id, FROZEN_NOW)

        stats = builder.get_trends(db_session, days=days)["headache"]

        assert stats["count"] == num_logs
        assert stats["avg_logs_per_day"] == expected_frequency

    # --- ownership ------------------------------------------------------------

    def test_requires_signed_in_user(self, db_session, builder, symptom):
        log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=1))
        token = current_username.set(None)
        try:
            with pytest.raises(ValueError, match="Authenticated username is required"):
                builder.get_trends(db_session)
        finally:
            current_username.reset(token)

    def test_excludes_other_users_logs(self, db_session, builder, symptom, other_user):
        log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=1), intensity=3)
        with _AsUser(other_user):
            their_symptom = SymptomRepository().create_symptom(
                db_session, SymptomCreate(name="rash", location="arm", sensation="itch")
            )
            log_symptom(db_session, their_symptom.id, FROZEN_NOW - timedelta(days=1), intensity=9)

        result = builder.get_trends(db_session)

        assert set(result) == {"headache"}
        assert result["headache"]["count"] == 1

    def test_other_user_sees_only_their_own_trends(self, db_session, builder, symptom, other_user):
        log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=1), intensity=3)
        with _AsUser(other_user):
            their_symptom = SymptomRepository().create_symptom(
                db_session, SymptomCreate(name="rash", location="arm", sensation="itch")
            )
            log_symptom(db_session, their_symptom.id, FROZEN_NOW - timedelta(days=1), intensity=9)

            result = builder.get_trends(db_session)

        assert set(result) == {"rash"}
        assert result["rash"]["max_intensity"] == 9

    # --- days guard (prevents ZeroDivisionError in avg_logs_per_day) -----------

    @pytest.mark.parametrize("days", [0, -1, -30])
    def test_non_positive_days_raises_value_error(self, db_session, builder, symptom, days):
        log_symptom(db_session, symptom.id, FROZEN_NOW - timedelta(days=1))

        with pytest.raises(ValueError):
            builder.get_trends(db_session, days=days)

    def test_days_zero_with_log_at_now_raises_value_error_not_zero_division(self, db_session, builder, symptom):
        # A log at exactly "now" is inside a 0-day window, so without the guard
        # avg_logs_per_day would compute len / 0.
        log_symptom(db_session, symptom.id, FROZEN_NOW)

        with pytest.raises(ValueError) as exc_info:
            builder.get_trends(db_session, days=0)

        assert not isinstance(exc_info.value, ZeroDivisionError)
        assert not isinstance(exc_info.value.__cause__, ZeroDivisionError)
        assert not isinstance(exc_info.value.__context__, ZeroDivisionError)


# --------------------------------------------------------------------------- #
# Not yet implemented
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "call",
    [
        pytest.param(lambda b, db: b.get_revealed_insights(db, uuid4()), id="get_revealed_insights"),
        pytest.param(lambda b, db: b.get_meal_ideas(db, uuid4(), FROZEN_NOW.date()), id="get_meal_ideas"),
        pytest.param(lambda b, db: b.adapt_recipe(db, uuid4(), {}, "make it dairy free"), id="adapt_recipe"),
        pytest.param(lambda b, db: b.get_profile_constraints(db, uuid4()), id="get_profile_constraints"),
        pytest.param(lambda b, db: b.draft_log_entry(db, uuid4(), "had pizza"), id="draft_log_entry"),
        pytest.param(
            lambda b, db: b.create_summary(db, uuid4(), FROZEN_NOW.date(), FROZEN_NOW.date()),
            id="create_summary",
        ),
    ],
)
def test_unimplemented_tools_raise(db_session, builder, call):
    with pytest.raises(NotImplementedError):
        call(builder, db_session)
