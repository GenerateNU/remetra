"""Integration tests for FamilyConfidenceService.apply_expected_reactions (the decrease)."""

from uuid import uuid4

import pytest
from sqlalchemy import delete

from analysis.model_constants import INITIAL_LOG_ODDS
from analysis.timing import meal_strength, timing_share
from models.component import Component
from models.ingredient import Ingredient
from models.ingredient_component import IngredientComponent
from models.symptom_family import SymptomFamily
from models.user import User
from models.user_background_total import UserBackgroundTotal
from models.user_family_confidence import UserFamilyConfidence
from repositories.family_confidence_repository import FamilyConfidenceRepository
from services.family_confidence_service import FamilyConfidenceService

FULL_SERVING_GI = meal_strength(SymptomFamily.GI, 1.0)


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


@pytest.fixture
def setup_ingredients(db_session):
    """A test user, a bread with two full-serving components, and a water whose only component is level 0."""
    for model in (UserFamilyConfidence, UserBackgroundTotal, Component):
        db_session.execute(delete(model))

    user = db_session.query(User).filter(User.username == "testuser").one_or_none()
    if not user:
        user = User(username="testuser", email="test@example.com")
        db_session.add(user)

    gluten = _component("gluten")
    fructans = _component("fructans")
    trace = _component("trace")
    bread = Ingredient(slug="test_bread", canonical_name="test bread")
    water = Ingredient(slug="test_water", canonical_name="test water")
    db_session.add_all([gluten, fructans, trace, bread, water])
    db_session.flush()

    db_session.add_all([_link(bread, gluten, 3), _link(bread, fructans, 3), _link(water, trace, 0)])
    db_session.flush()
    return user, bread, water, gluten, fructans


class TestApplyExpectedReactions:
    def test_full_gi_window_lowers_log_odds_by_meal_strength(self, db_session, setup_ingredients):
        """A full GI window (0-36 h) takes about 0.51 off the log-odds, taking 4% to about 2.4%."""
        user, bread, _, gluten, _ = setup_ingredients

        results = FamilyConfidenceService().apply_expected_reactions(
            db_session, user.username, bread.id, SymptomFamily.GI, 0, 36
        )

        assert len(results) == 2
        row = _row(db_session, user.username, SymptomFamily.GI, gluten)
        assert abs(row.log_odds - (INITIAL_LOG_ODDS - FULL_SERVING_GI)) < 1e-6
        for result in results:
            assert abs(result.confidence - 0.024) < 1e-3

    def test_expected_reactions_matches_log_odds_drop(self, db_session, setup_ingredients):
        """expected_reactions goes up by exactly what log_odds goes down."""
        user, bread, _, gluten, _ = setup_ingredients

        FamilyConfidenceService().apply_expected_reactions(db_session, user.username, bread.id, SymptomFamily.GI, 0, 10)

        row = _row(db_session, user.username, SymptomFamily.GI, gluten)
        assert row.expected_reactions > 0
        assert abs(row.expected_reactions - (INITIAL_LOG_ODDS - row.log_odds)) < 1e-9

    def test_only_decreases(self, db_session, setup_ingredients):
        """Every component's log-odds goes down, never up."""
        user, bread, _, gluten, fructans = setup_ingredients

        FamilyConfidenceService().apply_expected_reactions(db_session, user.username, bread.id, SymptomFamily.GI, 2, 20)

        for component in (gluten, fructans):
            assert _row(db_session, user.username, SymptomFamily.GI, component).log_odds < INITIAL_LOG_ODDS

    def test_same_level_components_get_identical_updates(self, db_session, setup_ingredients):
        """Two components at the same level and confidence lose the same amount."""
        user, bread, _, gluten, fructans = setup_ingredients

        FamilyConfidenceService().apply_expected_reactions(db_session, user.username, bread.id, SymptomFamily.GI, 0, 36)

        gluten_row = _row(db_session, user.username, SymptomFamily.GI, gluten)
        fructans_row = _row(db_session, user.username, SymptomFamily.GI, fructans)
        assert abs(gluten_row.log_odds - fructans_row.log_odds) < 1e-9

    def test_only_given_family_changes(self, db_session, setup_ingredients):
        """A GI decrease leaves SKIN and HEAD untouched."""
        user, bread, _, gluten, _ = setup_ingredients

        FamilyConfidenceService().apply_expected_reactions(db_session, user.username, bread.id, SymptomFamily.GI, 0, 36)

        for family in (SymptomFamily.SKIN, SymptomFamily.HEAD):
            row = _row(db_session, user.username, family, gluten)
            assert abs(row.log_odds - INITIAL_LOG_ODDS) < 1e-9
            assert row.expected_reactions == 0

    def test_splitting_span_matches_one_call(self, db_session, setup_ingredients):
        """0-10 plus 10-36 gives the same total decrease as one call over 0-36."""
        user, bread, _, gluten, _ = setup_ingredients
        service = FamilyConfidenceService()

        service.apply_expected_reactions(db_session, user.username, bread.id, SymptomFamily.GI, 0, 10)
        service.apply_expected_reactions(db_session, user.username, bread.id, SymptomFamily.GI, 10, 36)

        row = _row(db_session, user.username, SymptomFamily.GI, gluten)
        assert abs(row.log_odds - (INITIAL_LOG_ODDS - FULL_SERVING_GI)) < 1e-6

    def test_span_past_window_changes_nothing(self, db_session, setup_ingredients):
        """40-60 h is entirely past the GI window, so nothing changes."""
        user, bread, _, gluten, _ = setup_ingredients
        service = FamilyConfidenceService()
        service.ensure_initialized(db_session, user.username)

        results = service.apply_expected_reactions(db_session, user.username, bread.id, SymptomFamily.GI, 40, 60)

        assert results == []
        assert abs(_row(db_session, user.username, SymptomFamily.GI, gluten).log_odds - INITIAL_LOG_ODDS) < 1e-9

    def test_span_crossing_window_is_clamped(self, db_session, setup_ingredients):
        """30-50 h is clamped to 30-36 h for GI."""
        user, bread, _, gluten, _ = setup_ingredients

        FamilyConfidenceService().apply_expected_reactions(
            db_session, user.username, bread.id, SymptomFamily.GI, 30, 50
        )

        expected_drop = FULL_SERVING_GI * timing_share(SymptomFamily.GI, 30, 36)
        row = _row(db_session, user.username, SymptomFamily.GI, gluten)
        assert abs(row.log_odds - (INITIAL_LOG_ODDS - expected_drop)) < 1e-9

    def test_start_after_end_raises(self, db_session, setup_ingredients):
        user, bread, _, _, _ = setup_ingredients

        with pytest.raises(ValueError):
            FamilyConfidenceService().apply_expected_reactions(
                db_session, user.username, bread.id, SymptomFamily.GI, 10, 5
            )

    def test_unknown_ingredient_raises(self, db_session, setup_ingredients):
        user, _, _, _, _ = setup_ingredients

        with pytest.raises(ValueError):
            FamilyConfidenceService().apply_expected_reactions(
                db_session, user.username, uuid4(), SymptomFamily.GI, 0, 36
            )

    def test_only_level_zero_components_returns_empty(self, db_session, setup_ingredients):
        user, _, water, _, _ = setup_ingredients

        results = FamilyConfidenceService().apply_expected_reactions(
            db_session, user.username, water.id, SymptomFamily.GI, 0, 36
        )

        assert results == []

    def test_new_user_is_initialized_then_updated(self, db_session, setup_ingredients):
        """The first call for a user with no rows creates them, then applies the decrease."""
        user, bread, _, gluten, _ = setup_ingredients
        repo = FamilyConfidenceRepository()
        assert repo.has_confidences(db_session, user.username) is False

        FamilyConfidenceService().apply_expected_reactions(db_session, user.username, bread.id, SymptomFamily.GI, 0, 36)

        assert repo.has_confidences(db_session, user.username) is True
        assert _row(db_session, user.username, SymptomFamily.GI, gluten).log_odds < INITIAL_LOG_ODDS
