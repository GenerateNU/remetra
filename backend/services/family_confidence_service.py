"""Business logic for a user's per-family component confidences."""

import math
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from analysis.model_constants import LOOKBACK_HOURS
from analysis.model_constants import background_rate as compute_background_rate
from analysis.timing import expected_reaction_penalty, meal_strength, timing_share
from models.symptom_family import SymptomFamily
from repositories.family_confidence_repository import FamilyConfidenceRepository
from repositories.taxonomy_repository import TaxonomyRepository
from repositories.user_repository import UserRepository
from schemas.family_confidence import ComponentConfidenceResponse, FamilyConfidenceResponse

MAX_CONCENTRATION_LEVEL = 3


class FamilyConfidenceService:
    """Reads and updates how strongly each component is suspected of causing each symptom family."""

    def __init__(self):
        self.repo = FamilyConfidenceRepository()
        self.taxonomy_repo = TaxonomyRepository()
        self.user_repo = UserRepository()

    def ensure_initialized(self, db: Session, username: str) -> None:
        """Create the user's starting confidence and background rows if they have none yet."""
        if not self.repo.has_confidences(db, username):
            self.repo.initialize_for_user(db, username)

    def _component_exposures(self, db: Session, ingredient_id: UUID) -> dict[UUID, float]:
        """Return each of the ingredient's components mapped to its exposure e_c for one standard serving.

        e_c = min(1, concentration_level / 3). Level-0 components are left out, since they can't contribute.
        Raises ValueError if the ingredient doesn't exist.
        """
        components = self.taxonomy_repo.get_components_for_ingredient_id(db, ingredient_id)
        if components is None:
            raise ValueError(f"Unknown ingredient {ingredient_id}")
        return {
            component_id: min(1.0, concentration_level / MAX_CONCENTRATION_LEVEL)
            for component_id, concentration_level in components
            if concentration_level > 0
        }

    def _meal_strengths(self, family: SymptomFamily, exposures: dict[UUID, float]) -> dict[UUID, float]:
        """Return each component mapped to its meal strength a_{c,f}: expected family reactions if it's a trigger."""
        return {component_id: meal_strength(family, exposure) for component_id, exposure in exposures.items()}

    def get_family_confidences(self, db: Session, username: str) -> list[FamilyConfidenceResponse]:
        """Return every (component, family) pair with its confidence q = sigmoid(log_odds)."""
        rows = self.repo.get_all_confidences(db, username)
        return [
            FamilyConfidenceResponse(
                component_slug=row.component.slug,
                family=row.family,
                confidence=1.0 / (1.0 + math.exp(-row.log_odds)),
            )
            for row in rows
        ]

    def get_component_confidences(self, db: Session, username: str) -> list[ComponentConfidenceResponse]:
        """Return one row per component with Q_c = 1 - product(1 - q_{c,f}) across all families."""
        rows = self.repo.get_all_confidences(db, username)
        by_component: dict[str, float] = {}
        for row in rows:
            slug = row.component.slug
            q_f = 1.0 / (1.0 + math.exp(-row.log_odds))
            by_component[slug] = by_component.get(slug, 1.0) * (1.0 - q_f)
        return [
            ComponentConfidenceResponse(component_slug=slug, confidence=1.0 - product)
            for slug, product in by_component.items()
        ]

    def get_background_rate(self, db: Session, username: str, family: SymptomFamily, since: datetime) -> float:
        """Return the hourly background rate for a family, mixing prior with observed data."""
        user = self.user_repo.get_by_username(db, username)
        if user is None:
            raise ValueError(f"Unknown user {username}")
        created_at = user.created_at.replace(tzinfo=timezone.utc) if user.created_at.tzinfo is None else user.created_at
        if since.tzinfo is None:
            since = since.replace(tzinfo=timezone.utc)
        if since < created_at:
            raise ValueError("since is before user creation")
        now = datetime.now(timezone.utc)
        hours_observed = (now - since).total_seconds() / 3600
        background_total = self.repo.get_background_total(db, username, family)
        return compute_background_rate(family, background_total, hours_observed)

    def apply_expected_reactions(
        self,
        db: Session,
        username: str,
        ingredient_id: UUID,
        family: SymptomFamily,
        start_hours: float,
        end_hours: float,
    ) -> list[FamilyConfidenceResponse]:
        """Lower confidences for the ingredient's component for the part of its timing window
        between 'start_hours' and 'end_hours' after eating.

        Returns the updated confidences for the components that changed.
        """
        if start_hours > end_hours:
            raise ValueError(f"start_hours ({start_hours}) cannot be after end_hours ({end_hours})")
        span_start = max(0.0, start_hours)
        span_end = min(LOOKBACK_HOURS[family], end_hours)
        if span_start >= span_end:
            return []

        self.ensure_initialized(db, username)
        strengths = self._meal_strengths(family, self._component_exposures(db, ingredient_id))
        if not strengths:
            return []

        share = timing_share(family, span_start, span_end)
        penalties = expected_reaction_penalty(strengths, share)
        expected = {component_id: -penalty for component_id, penalty in penalties.items()}

        try:
            self.repo.update_log_odds(db, username, family, penalties, commit=False)
            self.repo.add_expected_reactions(db, username, family, expected, commit=False)
            db.commit()
        except Exception:
            db.rollback()
            raise

        return self._confidence_responses(db, username, family, list(penalties))

    def _confidence_responses(
        self, db: Session, username: str, family: SymptomFamily, component_ids: list[UUID]
    ) -> list[FamilyConfidenceResponse]:
        """Return the current confidences for the given components, with q = 1 / (1 + e^{-log_odds})."""
        rows = self.repo.get_confidences(db, username, family, component_ids)
        return [
            FamilyConfidenceResponse(
                component_slug=row.component.slug,
                family=row.family,
                confidence=1 / (1 + math.exp(-row.log_odds)),
            )
            for row in rows
        ]
