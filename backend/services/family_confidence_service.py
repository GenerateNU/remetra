"""Business logic for a user's per-family component confidences."""

import math
from collections import defaultdict
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from analysis.model_constants import LOOKBACK_HOURS, background_rate
from analysis.timing import expected_reaction_penalty, meal_strength, symptom_evidence, timing_density, timing_share
from models.symptom_family import MODELED_FAMILIES, SymptomFamily
from models.user_family_confidence import UserFamilyConfidence
from repositories.family_confidence_repository import FamilyConfidenceRepository
from repositories.symptom_repository import SymptomRepository
from repositories.taxonomy_repository import TaxonomyRepository
from repositories.user_repository import UserRepository
from schemas.family_confidence import ComponentConfidenceResponse, FamilyConfidenceResponse
from services.symptom_routing import route_symptom

MAX_CONCENTRATION_LEVEL = 3


class FamilyConfidenceService:
    """Reads and updates how strongly each component is suspected of causing each symptom family."""

    def __init__(self):
        self.repo = FamilyConfidenceRepository()
        self.taxonomy_repo = TaxonomyRepository()
        self.symptom_repo = SymptomRepository()
        self.user_repo = UserRepository()

    def ensure_initialized(self, db: Session, username: str) -> None:
        """Initialize 120 confidence rows + 3 background rows if the user has none."""
        if not self.repo.has_confidences(db, username):
            self.repo.initialize_for_user(db, username)

    def get_family_confidences(self, db: Session, username: str) -> list[FamilyConfidenceResponse]:
        """Return q = 1 / (1 + e^{-log_odds}) for each (component, family) pair."""
        rows = self.repo.get_all_confidences(db, username)
        return [_to_response(row) for row in rows]

    def get_component_confidences(self, db: Session, username: str) -> list[ComponentConfidenceResponse]:
        """Return Q_c = 1 - prod_f(1 - q_{c,f}) for each component."""
        rows = self.repo.get_all_confidences(db, username)

        by_component: dict[str, dict[str, float]] = defaultdict(dict)
        for row in rows:
            by_component[row.component.slug][row.family] = _to_probability(row.log_odds)

        results = []
        for slug, family_qs in by_component.items():
            product = 1.0
            for f in MODELED_FAMILIES:
                product *= 1.0 - family_qs.get(f.value, 0.0)
            results.append(
                ComponentConfidenceResponse(
                    component_slug=slug,
                    confidence=1.0 - product,
                )
            )
        return results

    def get_background_rate(self, db: Session, username: str, family: SymptomFamily, as_of: datetime) -> float:
        """Compute lambda_f using the prior-weighted formula from the spec."""
        user = self.user_repo.get_by_username(db, username)
        if user is None:
            raise ValueError(f"User '{username}' not found")
        if as_of < user.created_at:
            raise ValueError("as_of is before user creation")

        hours_observed = (as_of - user.created_at).total_seconds() / 3600.0
        background_total = self.repo.get_background_total(db, username, family)

        return background_rate(family, background_total, hours_observed)

    def _component_exposures(self, db: Session, ingredient_id: UUID) -> dict[UUID, float]:
        """Return each of the ingredient's components mapped to its exposure level e_c for one standard serving.

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

    def apply_symptom_evidence(
        self,
        db: Session,
        username: str,
        ingredient_id: UUID,
        symptom_id: UUID,
        hours_elapsed: float,
    ) -> list[FamilyConfidenceResponse]:
        """Raise confidences for the ingredient's components after a symptom `hours_elapsed` hours after eating it.

        Each component gains log-odds by how well it explains the symptom compared with the background rate and
        the ingredient's other components. Only rows for the symptom's family change. The family comes from
        symptom routing (location + sensation); it is not stored on the symptom.

        Returns the updated confidences for the components that changed, or [] if nothing changed: the symptom
        routes to no modeled family, the symptom is outside the family's timing window, or the ingredient has
        only level-0 components. Raises ValueError if the symptom doesn't exist or belongs to another user, or if
        the ingredient doesn't exist.
        """
        symptom = self.symptom_repo.get_symptom_by_id(db, symptom_id)
        if symptom is None or symptom.username != username:
            raise ValueError(f"Symptom {symptom_id} not found for user {username}")
        family = route_symptom(symptom.sensation, symptom.location).family
        if family not in MODELED_FAMILIES:
            return []

        if hours_elapsed <= 0 or hours_elapsed > LOOKBACK_HOURS[family]:
            return []

        self.ensure_initialized(db, username)
        exposures = self._component_exposures(db, ingredient_id)
        if not exposures:
            return []
        strengths = self._meal_strengths(family, exposures)

        # If this food causes a reaction, how likely is it to start at exactly this hour after eating?
        density = timing_density(family, hours_elapsed)
        # If this component is a trigger, how many reactions per hour would it cause at the hour the symptom started?
        pulls = {component_id: strength * density for component_id, strength in strengths.items()}

        rows = self.repo.get_confidences(db, username, family, component_ids=list(pulls))
        confidences = {row.component_id: _to_probability(row.log_odds) for row in rows}
        rate = self.get_background_rate(db, username, family, as_of=datetime.now(timezone.utc))

        deltas = symptom_evidence(pulls, confidences, rate)
        self.repo.update_log_odds(db, username, family, deltas)

        # update_log_odds commits, which expires `rows`, so reading them again loads the new log_odds.
        return [_to_response(row) for row in rows]

    def apply_expected_reactions(
        self,
        db: Session,
        username: str,
        ingredient_id: UUID,
        family: SymptomFamily,
        start_hours: float,
        end_hours: float,
    ) -> list[FamilyConfidenceResponse]:
        """Lower confidences for the ingredient's components for the part of its timing window
        between `start_hours` and `end_hours` after eating.

        Returns the updated confidences for the components that changed. Raises ValueError if the family isn't
        modeled or `start_hours` is after `end_hours`.
        """
        if family not in MODELED_FAMILIES:
            raise ValueError(f"Family {family} has no confidences")
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

        rows = self.repo.get_confidences(db, username, family, list(penalties))
        return [_to_response(row) for row in rows]


def _to_probability(log_odds: float) -> float:
    """Convert log-odds to a probability: q = 1 / (1 + e^-l)."""
    return 1.0 / (1.0 + math.exp(-log_odds))


def _to_response(row: UserFamilyConfidence) -> FamilyConfidenceResponse:
    """Build the response for one confidence row, with its component slug and confidence as a probability."""
    return FamilyConfidenceResponse(
        component_slug=row.component.slug,
        family=row.family,
        confidence=_to_probability(row.log_odds),
    )
