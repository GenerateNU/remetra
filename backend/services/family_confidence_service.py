"""Business logic for a user's per-family component confidences."""

from uuid import UUID

from sqlalchemy.orm import Session

from analysis.timing import meal_strength
from models.symptom_family import SymptomFamily
from repositories.family_confidence_repository import FamilyConfidenceRepository
from repositories.taxonomy_repository import TaxonomyRepository

MAX_CONCENTRATION_LEVEL = 3


class FamilyConfidenceService:
    """Reads and updates how strongly each component is suspected of causing each symptom family."""

    def __init__(self):
        self.repo = FamilyConfidenceRepository()
        self.taxonomy_repo = TaxonomyRepository()

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
