import math
from collections import defaultdict
from datetime import datetime

from sqlalchemy.orm import Session

from analysis.model_constants import background_rate
from models.symptom_family import SymptomFamily
from repositories.family_confidence_repository import FamilyConfidenceRepository
from repositories.user_repository import UserRepository
from schemas.family_confidence import ComponentConfidenceResponse, FamilyConfidenceResponse


class FamilyConfidenceService:
    def __init__(self):
        self.repo = FamilyConfidenceRepository()
        self.user_repo = UserRepository()

    def ensure_initialized(self, db: Session, username: str) -> None:
        """Initialize 120 confidence rows + 3 background rows if the user has none."""
        if not self.repo.has_confidences(db, username):
            self.repo.initialize_for_user(db, username)

    def get_family_confidences(self, db: Session, username: str) -> list[FamilyConfidenceResponse]:
        """Return q = 1 / (1 + e^{-log_odds}) for each (component, family) pair."""
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
        """Return Q_c = 1 - prod_f(1 - q_{c,f}) for each component."""
        rows = self.repo.get_all_confidences(db, username)

        by_component: dict[str, dict[str, float]] = defaultdict(dict)
        for row in rows:
            q = 1.0 / (1.0 + math.exp(-row.log_odds))
            by_component[row.component.slug][row.family] = q

        results = []
        for slug, family_qs in by_component.items():
            product = 1.0
            for f in SymptomFamily:
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
