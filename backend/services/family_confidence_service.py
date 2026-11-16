"""Business logic for a user's per-family component confidences."""

import math
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from analysis.model_constants import TIMING_WINDOW_HOURS
from analysis.timing import meal_strength, symptom_evidence, timing_density
from models.symptom_family import SymptomFamily
from models.user_family_confidence import UserFamilyConfidence
from repositories.family_confidence_repository import FamilyConfidenceRepository
from repositories.symptom_repository import SymptomRepository
from repositories.taxonomy_repository import TaxonomyRepository
from schemas.family_confidence import FamilyConfidenceResponse

MAX_CONCENTRATION_LEVEL = 3


class FamilyConfidenceService:
    """Reads and updates how strongly each component is suspected of causing each symptom family."""

    def __init__(self):
        self.repo = FamilyConfidenceRepository()
        self.taxonomy_repo = TaxonomyRepository()
        self.symptom_repo = SymptomRepository()

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
        the ingredient's other components. Only rows for the symptom's family change.

        Returns the updated confidences for the components that changed, or [] if nothing changed: the symptom
        has no family, the symptom is outside the family's timing window, or the ingredient has only level-0
        components. Raises ValueError if the symptom doesn't exist or belongs to another user, or if the
        ingredient doesn't exist.
        """
        symptom = self.symptom_repo.get_symptom_by_id(db, symptom_id)
        if symptom is None or symptom.username != username:
            raise ValueError(f"Symptom {symptom_id} not found for user {username}")
        if symptom.family is None:
            return []
        family = SymptomFamily(symptom.family)

        if hours_elapsed <= 0 or hours_elapsed > TIMING_WINDOW_HOURS[family]:
            return []

        self.ensure_initialized(db, username)
        exposures = self._component_exposures(db, ingredient_id)
        if not exposures:
            return []
        strengths = self._meal_strengths(family, exposures)

        density = timing_density(family, hours_elapsed)
        pulls = {component_id: strength * density for component_id, strength in strengths.items()}

        rows = self.repo.get_confidences(db, username, family, component_ids=list(pulls))
        confidences = {row.component_id: _to_probability(row.log_odds) for row in rows}
        background_rate = self.get_background_rate(db, username, family, as_of=datetime.now(timezone.utc))

        deltas = symptom_evidence(pulls, confidences, background_rate)
        self.repo.update_log_odds(db, username, family, deltas)

        # update_log_odds commits, which expires `rows`, so reading them again loads the new log_odds.
        return [_to_response(row) for row in rows]


def _to_probability(log_odds: float) -> float:
    """Convert log-odds to a probability: q = 1 / (1 + e^-l)."""
    return 1 / (1 + math.exp(-log_odds))


def _to_response(row: UserFamilyConfidence) -> FamilyConfidenceResponse:
    """Build the response for one confidence row, with its component slug and confidence as a probability."""
    return FamilyConfidenceResponse(
        component_id=row.component_id,
        component_slug=row.component.slug,
        family=row.family,
        confidence=_to_probability(row.log_odds),
    )
