"""Integration tests for the family confidence repository and service."""

import math
from datetime import datetime, timezone

import pytest
from sqlalchemy import delete

from analysis.model_constants import INITIAL_LOG_ODDS, P0
from models.component import Component
from models.symptom_family import SymptomFamily
from models.user import User
from models.user_background_total import UserBackgroundTotal
from models.user_family_confidence import UserFamilyConfidence
from repositories.family_confidence_repository import FamilyConfidenceRepository


def _component(slug: str) -> Component:
    return Component(
        slug=slug,
        display_name=slug,
        category="fodmap",
        inclusion_confidence="high",
        prior_tier="high",
    )


@pytest.fixture
def setup_user_and_components(db_session):
    """Create a test user and 2 components. Cleans existing rows first."""
    for model in (UserFamilyConfidence, UserBackgroundTotal, Component):
        db_session.execute(delete(model))

    user = db_session.query(User).filter(User.username == "testuser").one_or_none()
    if not user:
        user = User(username="testuser", email="test@example.com")
        db_session.add(user)

    gluten = _component("gluten")
    lactose = _component("lactose")
    db_session.add_all([gluten, lactose])
    db_session.flush()
    return user, gluten, lactose


class TestFamilyConfidenceRepository:
    def test_initialize_creates_rows(self, db_session, setup_user_and_components):
        user, gluten, lactose = setup_user_and_components
        repo = FamilyConfidenceRepository()

        repo.initialize_for_user(db_session, user.username)

        confidences = repo.get_all_confidences(db_session, user.username)
        assert len(confidences) == 6  # 2 components x 3 families

    def test_initialize_is_idempotent(self, db_session, setup_user_and_components):
        user, _, _ = setup_user_and_components
        repo = FamilyConfidenceRepository()

        repo.initialize_for_user(db_session, user.username)
        repo.initialize_for_user(db_session, user.username)

        confidences = repo.get_all_confidences(db_session, user.username)
        assert len(confidences) == 6

    def test_initial_log_odds_value(self, db_session, setup_user_and_components):
        user, _, _ = setup_user_and_components
        repo = FamilyConfidenceRepository()

        repo.initialize_for_user(db_session, user.username)

        confidences = repo.get_all_confidences(db_session, user.username)
        for row in confidences:
            assert abs(row.log_odds - INITIAL_LOG_ODDS) < 1e-6

    def test_background_totals_created(self, db_session, setup_user_and_components):
        user, _, _ = setup_user_and_components
        repo = FamilyConfidenceRepository()

        repo.initialize_for_user(db_session, user.username)

        for family in SymptomFamily:
            total = repo.get_background_total(db_session, user.username, family)
            assert total == 0.0

    def test_has_confidences_false_before_init(self, db_session, setup_user_and_components):
        user, _, _ = setup_user_and_components
        repo = FamilyConfidenceRepository()

        assert repo.has_confidences(db_session, user.username) is False

    def test_has_confidences_true_after_init(self, db_session, setup_user_and_components):
        user, _, _ = setup_user_and_components
        repo = FamilyConfidenceRepository()

        repo.initialize_for_user(db_session, user.username)
        assert repo.has_confidences(db_session, user.username) is True

    def test_get_confidences_filters_by_family(self, db_session, setup_user_and_components):
        user, _, _ = setup_user_and_components
        repo = FamilyConfidenceRepository()

        repo.initialize_for_user(db_session, user.username)

        gi_rows = repo.get_confidences(db_session, user.username, SymptomFamily.GI)
        assert len(gi_rows) == 2
        for row in gi_rows:
            assert row.family == "GI"

    def test_get_confidences_filters_by_component_ids(self, db_session, setup_user_and_components):
        user, gluten, lactose = setup_user_and_components
        repo = FamilyConfidenceRepository()

        repo.initialize_for_user(db_session, user.username)

        rows = repo.get_confidences(db_session, user.username, SymptomFamily.GI, [gluten.id])
        assert len(rows) == 1

    def test_update_log_odds(self, db_session, setup_user_and_components):
        user, gluten, _ = setup_user_and_components
        repo = FamilyConfidenceRepository()

        repo.initialize_for_user(db_session, user.username)
        repo.update_log_odds(db_session, user.username, SymptomFamily.GI, {gluten.id: 1.5})

        rows = repo.get_confidences(db_session, user.username, SymptomFamily.GI, [gluten.id])
        assert abs(rows[0].log_odds - (INITIAL_LOG_ODDS + 1.5)) < 1e-6

    def test_add_expected_reactions(self, db_session, setup_user_and_components):
        user, gluten, _ = setup_user_and_components
        repo = FamilyConfidenceRepository()

        repo.initialize_for_user(db_session, user.username)
        repo.add_expected_reactions(db_session, user.username, SymptomFamily.GI, {gluten.id: 0.5})

        rows = repo.get_confidences(db_session, user.username, SymptomFamily.GI, [gluten.id])
        assert abs(rows[0].expected_reactions - 0.5) < 1e-6

    def test_add_background_total(self, db_session, setup_user_and_components):
        user, _, _ = setup_user_and_components
        repo = FamilyConfidenceRepository()

        repo.initialize_for_user(db_session, user.username)
        repo.add_background_total(db_session, user.username, SymptomFamily.GI, 2.5)

        total = repo.get_background_total(db_session, user.username, SymptomFamily.GI)
        assert abs(total - 2.5) < 1e-6

    def test_background_total_returns_zero_without_init(self, db_session, setup_user_and_components):
        user, _, _ = setup_user_and_components
        repo = FamilyConfidenceRepository()

        total = repo.get_background_total(db_session, user.username, SymptomFamily.GI)
        assert total == 0.0


class TestFamilyConfidenceService:
    def test_ensure_initialized_creates_rows(self, db_session, setup_user_and_components):
        user, _, _ = setup_user_and_components
        from services.family_confidence_service import FamilyConfidenceService

        service = FamilyConfidenceService()
        service.ensure_initialized(db_session, user.username)

        repo = FamilyConfidenceRepository()
        assert repo.has_confidences(db_session, user.username) is True

    def test_ensure_initialized_is_idempotent(self, db_session, setup_user_and_components):
        user, _, _ = setup_user_and_components
        from services.family_confidence_service import FamilyConfidenceService

        service = FamilyConfidenceService()
        service.ensure_initialized(db_session, user.username)
        service.ensure_initialized(db_session, user.username)

        repo = FamilyConfidenceRepository()
        assert len(repo.get_all_confidences(db_session, user.username)) == 6

    def test_get_background_rate_new_user(self, db_session, setup_user_and_components):
        user, _, _ = setup_user_and_components
        from analysis.model_constants import initial_background_rate
        from services.family_confidence_service import FamilyConfidenceService

        service = FamilyConfidenceService()
        repo = FamilyConfidenceRepository()
        repo.initialize_for_user(db_session, user.username)

        rate = service.get_background_rate(db_session, user.username, SymptomFamily.GI, user.created_at)
        expected = initial_background_rate(SymptomFamily.GI)
        assert abs(rate - expected) < 1e-6

    def test_get_family_confidences_returns_all_pairs(self, db_session, setup_user_and_components):
        user, _, _ = setup_user_and_components
        from services.family_confidence_service import FamilyConfidenceService

        service = FamilyConfidenceService()
        service.ensure_initialized(db_session, user.username)

        results = service.get_family_confidences(db_session, user.username)
        assert len(results) == 6  # 2 components x 3 families

    def test_get_family_confidences_computes_q_from_log_odds(self, db_session, setup_user_and_components):
        user, _, _ = setup_user_and_components
        from services.family_confidence_service import FamilyConfidenceService

        service = FamilyConfidenceService()
        service.ensure_initialized(db_session, user.username)

        results = service.get_family_confidences(db_session, user.username)
        expected_q = 1.0 / (1.0 + math.exp(-INITIAL_LOG_ODDS))
        for r in results:
            assert abs(r.confidence - expected_q) < 1e-6
            assert abs(r.confidence - P0) < 1e-6  # should be 0.04

    def test_get_family_confidences_has_component_slug_and_family(self, db_session, setup_user_and_components):
        user, _, _ = setup_user_and_components
        from services.family_confidence_service import FamilyConfidenceService

        service = FamilyConfidenceService()
        service.ensure_initialized(db_session, user.username)

        results = service.get_family_confidences(db_session, user.username)
        slugs = {r.component_slug for r in results}
        families = {r.family for r in results}
        assert slugs == {"gluten", "lactose"}
        assert families == {"GI", "SKIN", "HEAD"}

    def test_get_component_confidences_returns_one_per_component(self, db_session, setup_user_and_components):
        user, _, _ = setup_user_and_components
        from services.family_confidence_service import FamilyConfidenceService

        service = FamilyConfidenceService()
        service.ensure_initialized(db_session, user.username)

        results = service.get_component_confidences(db_session, user.username)
        assert len(results) == 2
        slugs = {r.component_slug for r in results}
        assert slugs == {"gluten", "lactose"}

    def test_get_component_confidences_formula(self, db_session, setup_user_and_components):
        """Three families at 4% gives Q_c = 1 - (0.96)^3 ≈ 0.1153."""
        user, _, _ = setup_user_and_components
        from services.family_confidence_service import FamilyConfidenceService

        service = FamilyConfidenceService()
        service.ensure_initialized(db_session, user.username)

        results = service.get_component_confidences(db_session, user.username)
        expected_q = 1.0 - (1.0 - P0) ** 3  # ~0.1153
        for r in results:
            assert abs(r.confidence - expected_q) < 1e-4

    def test_get_component_confidence_increases_with_log_odds(self, db_session, setup_user_and_components):
        user, gluten, _ = setup_user_and_components
        from services.family_confidence_service import FamilyConfidenceService

        service = FamilyConfidenceService()
        repo = FamilyConfidenceRepository()
        repo.initialize_for_user(db_session, user.username)

        results = service.get_component_confidences(db_session, user.username)
        before = [r for r in results if r.component_slug == "gluten"][0]

        repo.update_log_odds(db_session, user.username, SymptomFamily.GI, {gluten.id: 3.0})

        results = service.get_component_confidences(db_session, user.username)
        after = [r for r in results if r.component_slug == "gluten"][0]
        assert after.confidence > before.confidence

    def test_get_background_rate_raises_if_before_creation(self, db_session, setup_user_and_components):
        user, _, _ = setup_user_and_components
        from services.family_confidence_service import FamilyConfidenceService

        service = FamilyConfidenceService()

        early = datetime(2000, 1, 1, tzinfo=timezone.utc)
        with pytest.raises(ValueError, match="before user creation"):
            service.get_background_rate(db_session, user.username, SymptomFamily.GI, early)

    def test_get_background_rate_raises_if_user_missing(self, db_session, setup_user_and_components):
        from services.family_confidence_service import FamilyConfidenceService

        service = FamilyConfidenceService()

        with pytest.raises(ValueError, match="not found"):
            service.get_background_rate(db_session, "no_such_user", SymptomFamily.GI, datetime.now(timezone.utc))
