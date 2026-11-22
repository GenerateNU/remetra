"""Integration tests for UserComponentStateRepository and OnboardingService."""

import math
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
import yaml

from analysis.model_constants import INITIAL_LOG_ODDS
from auth_context import current_username, system_access
from models.component import Component
from models.symptom import Symptom
from models.symptom_family import MODELED_FAMILIES, SymptomFamily
from models.symptom_log import SymptomLog
from repositories.food_log_repository import FoodLogRepository
from repositories.user_component_state_repository import UserComponentStateRepository
from schemas.food_log import FoodLogCreate
from services.onboarding_service import CONDITION_FILE, OnboardingService

COMPONENTS_FILE = CONDITION_FILE.parent / "components.yaml"

T0 = datetime(2025, 3, 1, 3, 0, tzinfo=timezone.utc)  # pinned "last update" after seeding
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


def _stored_last_updates(db_session, repo, username):
    """last_update values as stored in the database, not the session cache."""
    db_session.expire_all()
    return {s.last_update for s in repo.get_states_for_user(db_session, username)}


@pytest.fixture(autouse=True)
def components(db_session):
    """Load the 40 taxonomy components; the test database starts with none."""
    repo = UserComponentStateRepository()
    existing = repo.get_all_components(db_session)
    if existing:
        return existing

    columns = set(Component.__table__.columns.keys())
    with open(COMPONENTS_FILE) as f:
        entries = yaml.safe_load(f)["components"]
    for entry in entries:
        values = {k: v for k, v in entry.items() if k != "id" and k in columns}
        db_session.add(Component(slug=entry["id"], **values))
    db_session.flush()
    return repo.get_all_components(db_session)


@pytest.fixture
def seeded_user(db_session, authenticated_user):
    """Authenticated user with seeded state, last_update pinned to T0."""
    username = authenticated_user["username"]
    service = OnboardingService()
    repo = UserComponentStateRepository()

    service.initialize_user_state(db_session, username)
    states = repo.get_states_for_user(db_session, username)
    _set_states(db_session, repo, username, {(s.component_id, s.family): {"last_update": T0} for s in states})

    stored = _stored_last_updates(db_session, repo, username)
    assert stored == {T0}, f"update_states did not persist last_update: {stored}"
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

    def test_update_states_persists_last_update(self, db_session, seeded_user):
        """A saved last_update survives a re-read from the database."""
        repo = UserComponentStateRepository()
        states = repo.get_states_for_user(db_session, seeded_user)
        for s in states:
            s.last_update = NIGHT_1

        repo.update_states(db_session, states)

        assert _stored_last_updates(db_session, repo, seeded_user) == {NIGHT_1}


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
        assert count == len(states) == len(components) * len(MODELED_FAMILIES)
        assert {(s.component_id, s.family) for s in states} == {(c.id, f) for c in components for f in MODELED_FAMILIES}

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

        base = INITIAL_LOG_ODDS
        slug_by_id = {c.id: c.slug for c in repo.get_all_components(db_session)}
        for s in repo.get_states_for_user(db_session, username):
            if slug_by_id[s.component_id] in condition["components"]:
                expected = base + math.log(condition["multiplier"])
            else:
                expected = base
            assert s.log_odds == pytest.approx(expected), slug_by_id[s.component_id]

    def test_new_rows_have_utc_last_update(self, db_session, authenticated_user):
        """Freshly seeded rows are stamped with the current UTC time."""
        username = authenticated_user["username"]
        before = datetime.now(timezone.utc)

        OnboardingService().initialize_user_state(db_session, username)

        after = datetime.now(timezone.utc)
        repo = UserComponentStateRepository()
        for stored in _stored_last_updates(db_session, repo, username):
            assert stored is not None
            assert before - timedelta(seconds=1) <= stored <= after + timedelta(seconds=1)


class TestRunUserNight:
    """Integration tests for OnboardingService.run_user_night."""

    def test_first_night_for_new_user(self, db_session, authenticated_user):
        """A user with no state is seeded, the night runs, and last_update moves to as_of."""
        username = authenticated_user["username"]
        repo = UserComponentStateRepository()
        as_of = datetime.now(timezone.utc) + timedelta(days=1)

        OnboardingService().run_user_night(db_session, username, as_of)

        assert _stored_last_updates(db_session, repo, username) == {as_of}

    def test_stamps_last_update(self, db_session, seeded_user, two_days_of_meals):
        """After a run every stored row has last_update == as_of."""
        repo = UserComponentStateRepository()

        OnboardingService().run_user_night(db_session, seeded_user, NIGHT_1)

        assert _stored_last_updates(db_session, repo, seeded_user) == {NIGHT_1}

    def test_stamps_last_update_with_no_logs(self, db_session, seeded_user):
        """A night with nothing logged still moves last_update forward."""
        repo = UserComponentStateRepository()

        OnboardingService().run_user_night(db_session, seeded_user, NIGHT_1)

        assert _stored_last_updates(db_session, repo, seeded_user) == {NIGHT_1}

    def test_same_night_twice_changes_nothing(self, db_session, seeded_user, two_days_of_meals):
        """Running the same night again leaves every stored value unchanged."""
        service = OnboardingService()
        repo = UserComponentStateRepository()
        service.run_user_night(db_session, seeded_user, NIGHT_1)
        db_session.expire_all()
        after_first = _snapshot(repo.get_states_for_user(db_session, seeded_user))

        service.run_user_night(db_session, seeded_user, NIGHT_1)

        db_session.expire_all()
        _assert_same_states(_snapshot(repo.get_states_for_user(db_session, seeded_user)), after_first)

    def test_late_run_for_earlier_night_is_a_no_op(self, db_session, seeded_user, two_days_of_meals):
        """A delayed job for a night already covered by catch-up changes nothing."""
        service = OnboardingService()
        repo = UserComponentStateRepository()
        service.run_user_night(db_session, seeded_user, NIGHT_2)
        db_session.expire_all()
        after_catch_up = _snapshot(repo.get_states_for_user(db_session, seeded_user))

        service.run_user_night(db_session, seeded_user, NIGHT_1)

        db_session.expire_all()
        _assert_same_states(_snapshot(repo.get_states_for_user(db_session, seeded_user)), after_catch_up)

    @pytest.mark.xfail(reason="nightly_refresh does not update states yet", strict=True)
    def test_missed_night_matches_running_every_night(self, db_session, seeded_user, two_days_of_meals):
        """Skipping a night and catching up ends in the same state as running both nights."""
        service = OnboardingService()
        repo = UserComponentStateRepository()
        initial = _snapshot(repo.get_states_for_user(db_session, seeded_user))

        # Missed night: jump straight to night 2.
        service.run_user_night(db_session, seeded_user, NIGHT_2)
        db_session.expire_all()
        caught_up = _snapshot(repo.get_states_for_user(db_session, seeded_user))

        # Rewind, then run both nights in order.
        _set_states(db_session, repo, seeded_user, initial)
        service.run_user_night(db_session, seeded_user, NIGHT_1)
        service.run_user_night(db_session, seeded_user, NIGHT_2)
        db_session.expire_all()
        every_night = _snapshot(repo.get_states_for_user(db_session, seeded_user))

        assert sum(v["exposure_count"] for v in every_night.values()) > 0, (
            "no exposures counted; created_food needs at least one component for this test to mean anything"
        )
        _assert_same_states(caught_up, every_night)


# (location, sensation) pairs that symptom_routing.yaml sends to each outcome
SYMPTOM_KINDS = {
    "gi": ("Abdomen", "Cramping"),
    "skin": ("Skin", "Itching"),
    "head": ("Head", "Throbbing"),
    "other": ("Joints", "Aching"),
    "red_flag": ("Chest", "Pain"),
}


@pytest.fixture
def log_symptom(db_session, authenticated_user):
    """Factory: log a symptom of the given kind at a time, returning the SymptomLog."""
    symptoms = {}

    def _log(kind, timestamp):
        if kind not in symptoms:
            location, sensation = SYMPTOM_KINDS[kind]
            symptom = Symptom(
                username=authenticated_user["username"], name=kind, location=location, sensation=sensation
            )
            db_session.add(symptom)
            db_session.flush()
            symptoms[kind] = symptom
        log = SymptomLog(
            username=authenticated_user["username"], symptom_id=symptoms[kind].id, intensity=5, timestamp=timestamp
        )
        db_session.add(log)
        db_session.flush()
        return log

    return _log


@pytest.fixture
def log_meal(db_session, created_food):
    """Factory: log a meal of created_food at a time, returning the FoodLog."""
    repo = FoodLogRepository()

    def _log(timestamp):
        return repo.create_food_log(db_session, FoodLogCreate(food_id=created_food.id, timestamp=timestamp))

    return _log


def _ids(logs):
    return {log.id for log in logs}


class TestCollectNightLogs:
    """Which logs a nightly run observes for the window (T0, NIGHT_1]."""

    def test_no_symptoms_reads_only_meals_since_last_update(self, db_session, seeded_user, log_meal):
        """With nothing to explain, meals before last_update are not read."""
        old = log_meal(T0 - timedelta(hours=2))
        new = log_meal(T0 + timedelta(hours=2))

        meals, symptoms = OnboardingService().collect_night_logs(db_session, seeded_user, T0, NIGHT_1)

        assert symptoms == []
        assert _ids(meals) == {new.id}
        assert old.id not in _ids(meals)

    def test_symptoms_before_last_update_are_not_observed(self, db_session, seeded_user, log_symptom):
        """A symptom at exactly last_update belongs to the previous night."""
        log_symptom("gi", T0)
        log_symptom("gi", T0 - timedelta(hours=3))

        _, symptoms = OnboardingService().collect_night_logs(db_session, seeded_user, T0, NIGHT_1)

        assert symptoms == []

    def test_gi_symptom_widens_meal_window_by_36h(self, db_session, seeded_user, log_meal, log_symptom):
        """A new symptom pulls in older meals that could have caused it, up to its lookback."""
        symptom_time = T0 + timedelta(hours=2)
        symptom = log_symptom("gi", symptom_time)
        inside = log_meal(symptom_time - timedelta(hours=36))
        outside = log_meal(symptom_time - timedelta(hours=36, seconds=1))

        meals, symptoms = OnboardingService().collect_night_logs(db_session, seeded_user, T0, NIGHT_1)

        assert [s.id for s in symptoms] == [symptom.id]
        assert symptoms[0].family == SymptomFamily.GI
        assert inside.id in _ids(meals)
        assert outside.id not in _ids(meals)

    def test_skin_symptom_widens_meal_window_by_48h(self, db_session, seeded_user, log_meal, log_symptom):
        symptom_time = T0 + timedelta(hours=2)
        log_symptom("skin", symptom_time)
        inside = log_meal(symptom_time - timedelta(hours=48))
        outside = log_meal(symptom_time - timedelta(hours=48, seconds=1))

        meals, _ = OnboardingService().collect_night_logs(db_session, seeded_user, T0, NIGHT_1)

        assert inside.id in _ids(meals)
        assert outside.id not in _ids(meals)

    def test_earliest_symptom_sets_the_window(self, db_session, seeded_user, log_meal, log_symptom):
        """Several symptoms: the window reaches back to whichever needs the oldest meals."""
        log_symptom("gi", T0 + timedelta(hours=20))
        log_symptom("head", T0 + timedelta(hours=1))
        meal = log_meal(T0 + timedelta(hours=1) - timedelta(hours=35))

        meals, symptoms = OnboardingService().collect_night_logs(db_session, seeded_user, T0, NIGHT_1)

        assert len(symptoms) == 2
        assert meal.id in _ids(meals)

    @pytest.mark.parametrize("kind", ["other", "red_flag"])
    def test_unmodeled_symptoms_are_ignored(self, db_session, seeded_user, log_meal, log_symptom, kind):
        """Symptoms with no family confidences neither count nor widen the meal window."""
        log_symptom(kind, T0 + timedelta(hours=2))
        old = log_meal(T0 - timedelta(hours=2))

        meals, symptoms = OnboardingService().collect_night_logs(db_session, seeded_user, T0, NIGHT_1)

        assert symptoms == []
        assert old.id not in _ids(meals)


class TestRunUserNightWithSymptoms:
    def test_passes_widened_logs_to_nightly_refresh(self, db_session, seeded_user, log_meal, log_symptom):
        """run_user_night hands nightly_refresh the window's symptoms and their candidate meals."""
        symptom = log_symptom("gi", T0 + timedelta(hours=2))
        meal = log_meal(T0 - timedelta(hours=10))

        with patch("services.onboarding_service.nightly_refresh") as refresh:
            OnboardingService().run_user_night(db_session, seeded_user, NIGHT_1)

        meals, symptoms, now, last_update, _states = refresh.call_args.args
        assert _ids(meals) == {meal.id}
        assert _ids(symptoms) == {symptom.id}
        assert (now, last_update) == (NIGHT_1, T0)

    def test_runs_with_real_symptoms(self, db_session, seeded_user, log_meal, log_symptom):
        """Regression: symptom_meal_map reads symptom.family, which raw SymptomLog rows lack."""
        log_symptom("skin", T0 + timedelta(hours=5))
        log_meal(T0 + timedelta(hours=1))
        repo = UserComponentStateRepository()

        OnboardingService().run_user_night(db_session, seeded_user, NIGHT_1)

        assert _stored_last_updates(db_session, repo, seeded_user) == {NIGHT_1}


class TestWithoutSignedInUser:
    """Seeding script and nightly jobs run with no request user, as scripts/seed_onboarding.py does."""

    @pytest.fixture
    def no_user(self, authenticated_user):
        token = current_username.set(None)
        yield authenticated_user["username"]
        current_username.reset(token)

    def test_owned_rows_are_hidden_without_system_access(self, db_session, seeded_user, no_user):
        """Why the script needs system_access(): the ownership filter hides every state row."""
        assert UserComponentStateRepository().has_state(db_session, no_user) is False

    def test_reseeding_under_system_access_is_a_no_op(self, db_session, seeded_user, no_user):
        with system_access():
            assert OnboardingService().initialize_user_state(db_session, no_user) == 0

    def test_run_user_night_under_system_access(self, db_session, seeded_user, log_meal):
        log_meal(T0 + timedelta(hours=2))  # logged while signed in, so the row has an owner
        repo = UserComponentStateRepository()
        token = current_username.set(None)
        try:
            with system_access():
                OnboardingService().run_user_night(db_session, seeded_user, NIGHT_1)
                assert _stored_last_updates(db_session, repo, seeded_user) == {NIGHT_1}
        finally:
            current_username.reset(token)
