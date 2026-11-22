"""Integration tests for FamilyConfidenceService.apply_symptom_evidence (the increase)."""

from uuid import uuid4

import pytest
from sqlalchemy import delete

from analysis.model_constants import INITIAL_LOG_ODDS
from auth_context import system_access
from models.component import Component
from models.ingredient import Ingredient
from models.ingredient_component import IngredientComponent
from models.symptom import Symptom
from models.symptom_family import SymptomFamily
from models.user import User
from models.user_background_total import UserBackgroundTotal
from models.user_family_confidence import UserFamilyConfidence
from repositories.family_confidence_repository import FamilyConfidenceRepository
from services.family_confidence_service import FamilyConfidenceService


def _component(slug: str) -> Component:
    return Component(
        slug=slug,
        display_name=slug,
        category="fodmap",
        inclusion_confidence="high",
        prior_tier="high",
    )


def _link(ingredient: Ingredient, component: Component, level: int) -> IngredientComponent:
    return IngredientComponent(
        ingredient_id=ingredient.id,
        component_id=component.id,
        concentration_level=level,
        confidence="high",
    )


def _row(db_session, username, family, component):
    return FamilyConfidenceRepository().get_confidences(db_session, username, family, [component.id])[0]


@pytest.fixture(autouse=True)
def _as_system():
    """The nightly job has no signed-in user, so it reads symptoms under system_access()."""
    with system_access():
        yield


@pytest.fixture
def setup_symptoms(db_session):
    """A test user, a bread (gluten level 3, fructans level 1), a level-0 water, and GI / non-modeled symptoms."""
    for model in (UserFamilyConfidence, UserBackgroundTotal, Component):
        db_session.execute(delete(model))

    user = db_session.query(User).filter(User.username == "testuser").one_or_none()
    if not user:
        user = User(username="testuser", email="test@example.com")
        db_session.add(user)
        db_session.flush()

    gluten = _component("gluten")
    fructans = _component("fructans")
    trace = _component("trace")
    bread = Ingredient(slug="test_bread", canonical_name="test bread")
    water = Ingredient(slug="test_water", canonical_name="test water")
    bloating = Symptom(username="testuser", name="Bloating", location="Abdomen", sensation="Bloating")
    knee_ache = Symptom(username="testuser", name="Knee ache", location="Knees", sensation="Aching")
    db_session.add_all([gluten, fructans, trace, bread, water, bloating, knee_ache])
    db_session.flush()

    db_session.add_all([_link(bread, gluten, 3), _link(bread, fructans, 1), _link(water, trace, 0)])
    db_session.flush()
    return user, bread, water, gluten, fructans, bloating, knee_ache


class TestApplySymptomEvidence:
    def test_gi_symptom_raises_gi_confidences(self, db_session, setup_symptoms):
        user, bread, _, gluten, fructans, bloating, _ = setup_symptoms

        results = FamilyConfidenceService().apply_symptom_evidence(db_session, user.username, bread.id, bloating.id, 4)

        assert len(results) == 2
        assert {r.family for r in results} == {SymptomFamily.GI}
        for component in (gluten, fructans):
            assert _row(db_session, user.username, SymptomFamily.GI, component).log_odds > INITIAL_LOG_ODDS

    def test_higher_exposure_gains_more(self, db_session, setup_symptoms):
        """Gluten (level 3) explains the symptom better than fructans (level 1)."""
        user, bread, _, gluten, fructans, bloating, _ = setup_symptoms

        FamilyConfidenceService().apply_symptom_evidence(db_session, user.username, bread.id, bloating.id, 4)

        gluten_row = _row(db_session, user.username, SymptomFamily.GI, gluten)
        fructans_row = _row(db_session, user.username, SymptomFamily.GI, fructans)
        assert gluten_row.log_odds > fructans_row.log_odds

    def test_only_symptom_family_changes(self, db_session, setup_symptoms):
        user, bread, _, gluten, _, bloating, _ = setup_symptoms

        FamilyConfidenceService().apply_symptom_evidence(db_session, user.username, bread.id, bloating.id, 4)

        for family in (SymptomFamily.SKIN, SymptomFamily.HEAD):
            assert abs(_row(db_session, user.username, family, gluten).log_odds - INITIAL_LOG_ODDS) < 1e-9

    def test_non_modeled_symptom_changes_nothing(self, db_session, setup_symptoms):
        user, bread, _, _, _, _, knee_ache = setup_symptoms

        results = FamilyConfidenceService().apply_symptom_evidence(db_session, user.username, bread.id, knee_ache.id, 4)

        assert results == []

    @pytest.mark.parametrize("hours", [0, -1, 37])
    def test_outside_timing_window_changes_nothing(self, db_session, setup_symptoms, hours):
        user, bread, _, _, _, bloating, _ = setup_symptoms

        results = FamilyConfidenceService().apply_symptom_evidence(
            db_session, user.username, bread.id, bloating.id, hours
        )

        assert results == []

    def test_only_level_zero_components_returns_empty(self, db_session, setup_symptoms):
        user, _, water, _, _, bloating, _ = setup_symptoms

        results = FamilyConfidenceService().apply_symptom_evidence(db_session, user.username, water.id, bloating.id, 4)

        assert results == []

    def test_unknown_symptom_raises(self, db_session, setup_symptoms):
        user, bread, _, _, _, _, _ = setup_symptoms

        with pytest.raises(ValueError, match="not found"):
            FamilyConfidenceService().apply_symptom_evidence(db_session, user.username, bread.id, uuid4(), 4)

    def test_other_users_symptom_raises(self, db_session, setup_symptoms):
        _, bread, _, _, _, bloating, _ = setup_symptoms

        with pytest.raises(ValueError, match="not found"):
            FamilyConfidenceService().apply_symptom_evidence(db_session, "someone_else", bread.id, bloating.id, 4)

    def test_unknown_ingredient_raises(self, db_session, setup_symptoms):
        user, _, _, _, _, bloating, _ = setup_symptoms

        with pytest.raises(ValueError, match="Unknown ingredient"):
            FamilyConfidenceService().apply_symptom_evidence(db_session, user.username, uuid4(), bloating.id, 4)


class TestApplyExpectedReactionsFamily:
    def test_other_family_raises(self, db_session, setup_symptoms):
        user, bread, _, _, _, _, _ = setup_symptoms

        with pytest.raises(ValueError, match="no confidences"):
            FamilyConfidenceService().apply_expected_reactions(
                db_session, user.username, bread.id, SymptomFamily.OTHER, 0, 36
            )
