"""Integration tests for UserComponentStateRepository and OnboardingService."""

import math
from datetime import datetime, timedelta

import pytest
import yaml

from repositories.food_log_repository import FoodLogRepository
from repositories.user_component_state_repository import UserComponentStateRepository
from schemas.food_log import FoodLogCreate
from services.onboarding_service import CONDITION_FILE, FAMILIES, OnboardingService

T0 = datetime(2025, 3, 1, 3, 0)  # pinned "last update" after seeding
NIGHT_1 = T0 + timedelta(days=1)
NIGHT_2 = T0 + timedelta(days=2)

STATE_FIELDS = (
    "log_odds",
    "expected_reactions",
    "exposure_count",
    "background_rate",
    "background_total",
    "hours_since_onboarding",
    "last_update",
)


def _logit(p):
    return math.log(p / (1 - p))


def _load_config():
    with open(CONDITION_FILE) as f:
        return yaml.safe_load(f)


def _snapshot(states):
    """Plain copy of every state's values, keyed by (component_id, family)."""
    return {(s.component_id, s.family): {f: getattr(s, f) for f in STATE_FIELDS} for s in states}


def _assert_same_states(actual, expected):
    assert actual.keys() == expected.keys()
    for key in expected:
        for field in STATE_FIELDS:
            a, e = actual[key][field], expected[key][field]
            if isinstance(e, float):
                assert a == pytest.approx(e), (key, field)
            else:
                assert a == e, (key, field)


def _set_states(db_session, repo, username, values_by_key):
    """Overwrite stored states, e.g. to pin last_update or rewind to a snapshot."""
    states = repo.get_states_for_user(db_session, username)
    for s in states:
        for field, value in values_by_key[(s.component_id, s.family)].items():
            setattr(s, field, value)
    repo.update_states(db_session, states)


@pytest.fixture
def seeded_user(db_session, authenticated_user):
    """Authenticated user with seeded state, last_update pinned to T0."""
    username = authenticated_user["username"]
    service = OnboardingService()
    repo = UserComponentStateRepository()

    service.initialize_user_state(db_session, username)
    states = repo.get_states_for_user(db_session, username)
    _set_states(db_session, repo, username, {(s.component_id, s.family): {"last_update": T0} for s in states})
    return username


@pytest.fixture
def two_days_of_meals(db_session, authenticated_user, created_food):
    """One meal on each of the two days after T0."""
    repo = FoodLogRepository()
    for ts in (T0 + timedelta(hours=10), T0 + timedelta(hours=34)):
        repo.create_food_log(db_session, FoodLogCreate(food_id=created_food.id, timestamp=ts))


class TestUserComponentStateRepository:
    """Integration tests for UserComponentStateRepository."""

    def test_all_components_present(self, db_session):
        """The 40 components from #152 are in the database."""
        repo = UserComponentStateRepository()

        assert len(repo.get_all_components(db_session)) == 40

    def test_has_state_false_before_seeding(self, db_session, authenticated_user):
        """A new user has no state."""
        repo = UserComponentStateRepository()

        assert repo.has_state(db_session, authenticated_user["username"]) is False

    def test_states_are_scoped_to_user(self, db_session, seeded_user):
        """Another user sees none of this user's state."""
        repo = UserComponentStateRepository()

        assert repo.get_states_for_user(db_session, "no_such_user") == []
        assert all(s.username == seeded_user for s in repo.get_states_for_user(db_session, seeded_user))


class TestConditionFile:
    """The condition data file agrees with the database."""

    def test_condition_components_exist(self, db_session):
        """Every component slug in condition_multipliers.yaml is a real component."""
        repo = UserComponentStateRepository()
        slugs = {c.slug for c in repo.get_all_components(db_session)}

        for name, condition in _load_config()["conditions"].items():
            missing = set(condition["components"]) - slugs
            assert not missing, f"{name}: unknown components {missing}"


class TestInitializeUserState:
    """Integration tests for OnboardingService.initialize_user_state."""

    def test_creates_rows_for_every_component_and_family(self, db_session, authenticated_user):
        """Seeding stores one row per component per family."""
        username = authenticated_user["username"]
        service = OnboardingService()
        repo = UserComponentStateRepository()
        components = repo.get_all_components(db_session)

        count = service.initialize_user_state(db_session, username)

        states = repo.get_states_for_user(db_session, username)
        assert count == len(states) == len(components) * len(FAMILIES)
        assert {(s.component_id, s.family) for s in states} == {
            (c.id, f) for c in components for f in FAMILIES
        }

    def test_seeding_twice_is_a_no_op(self, db_session, authenticated_user):
        """A second seed returns 0 and leaves the stored rows alone."""
        username = authenticated_user["username"]
        service = OnboardingService()
        repo = UserComponentStateRepository()
        service.initialize_user_state(db_session, username)
        before = _snapshot(repo.get_states_for_user(db_session, username))

        assert service.initialize_user_state(db_session, username) == 0
        _assert_same_states(_snapshot(repo.get_states_for_user(db_session, username)), before)

    def test_condition_multiplier_applied(self, db_session, authenticated_user):
        """A user's onboarding condition raises the starting confidence of its components only."""
        username = authenticated_user["username"]
        service = OnboardingService()
        repo = UserComponentStateRepository()
        config = _load_config()
        name, condition = next(iter(config["conditions"].items()))
        user = repo.get_user(db_session, username)
        user.disease = [name]
        db_session.flush()

        service.initialize_user_state(db_session, username)

        base = _logit(config["defaults"]["base_confidence"])
        slug_by_id = {c.id: c.slug for c in repo.get_all_components(db_session)}
        for s in repo.get_states_for_user(db_session, username):
            if slug_by_id[s.component_id] in condition["components"]:
                expected = base + math.log(condition["multiplier"])
            else:
                expected = base
            assert s.log_odds == pytest.approx(expected), slug_by_id[s.component_id]

    def test_new_rows_have_last_update(self, db_session, authenticated_user):
        """Freshly seeded rows have a last_update, so the first night can run."""
        username = authenticated_user["username"]
        OnboardingService().initialize_user_state(db_session, username)

        states = UserComponentStateRepository().get_states_for_user(db_session, username)
        assert all(s.last_update is not None for s in states)


class TestRunUserNight:
    """Integration tests for OnboardingService.run_user_night."""

    def test_first_night_for_new_user(self, db_session, authenticated_user):
        """A user with no state is seeded and the night runs without error."""
        username = authenticated_user["username"]
        as_of = datetime.utcnow() + timedelta(days=1)

        OnboardingService().run_user_night(db_session, username, as_of)

        states = UserComponentStateRepository().get_states_for_user(db_session, username)
        assert states
        assert all(s.last_update is not None for s in states)

    def test_stamps_last_update(self, db_session, seeded_user, two_days_of_meals):
        """After a run every stored row has last_update == as_of."""
        OnboardingService().run_user_night(db_session, seeded_user, NIGHT_1)

        states = UserComponentStateRepository().get_states_for_user(db_session, seeded_user)
        assert {s.last_update for s in states} == {NIGHT_1}

    def test_same_night_twice_changes_nothing(self, db_session, seeded_user, two_days_of_meals):
        """Running the same night again leaves every stored value unchanged."""
        service = OnboardingService()
        repo = UserComponentStateRepository()
        service.run_user_night(db_session, seeded_user, NIGHT_1)
        after_first = _snapshot(repo.get_states_for_user(db_session, seeded_user))

        service.run_user_night(db_session, seeded_user, NIGHT_1)

        _assert_same_states(_snapshot(repo.get_states_for_user(db_session, seeded_user)), after_first)

    def test_late_run_for_earlier_night_is_a_no_op(self, db_session, seeded_user, two_days_of_meals):
        """A delayed job for a night already covered by catch-up changes nothing."""
        service = OnboardingService()
        repo = UserComponentStateRepository()
        service.run_user_night(db_session, seeded_user, NIGHT_2)
        after_catch_up = _snapshot(repo.get_states_for_user(db_session, seeded_user))

        service.run_user_night(db_session, seeded_user, NIGHT_1)

        _assert_same_states(_snapshot(repo.get_states_for_user(db_session, seeded_user)), after_catch_up)

    def test_missed_night_matches_running_every_night(self, db_session, seeded_user, two_days_of_meals):
        """Skipping a night and catching up ends in the same state as running both nights."""
        service = OnboardingService()
        repo = UserComponentStateRepository()
        initial = _snapshot(repo.get_states_for_user(db_session, seeded_user))

        # Missed night: jump straight to night 2.
        service.run_user_night(db_session, seeded_user, NIGHT_2)
        caught_up = _snapshot(repo.get_states_for_user(db_session, seeded_user))

        # Rewind, then run both nights in order.
        _set_states(db_session, repo, seeded_user, initial)
        service.run_user_night(db_session, seeded_user, NIGHT_1)
        service.run_user_night(db_session, seeded_user, NIGHT_2)
        every_night = _snapshot(repo.get_states_for_user(db_session, seeded_user))

        assert sum(v["exposure_count"] for v in every_night.values()) > 0, (
            "no exposures counted; created_food needs at least one component for this test to mean anything"
        )
        _assert_same_states(caught_up, every_night)