from sqlalchemy.orm import Session

from repositories.taxonomy_repository import TaxonomyRepository


class TaxonomyService:
    """Business logic for the ingredient/component taxonomy."""

    def __init__(self):
        self.repo = TaxonomyRepository()

    def get_components(self, db: Session, ingredient: str) -> list[dict]:
        """Return all components (with concentration_level) for an ingredient, matched by slug or canonical_name."""
        return [
            {"component": slug, "concentration_level": level}
            for slug, level in self.repo.get_components_for_ingredient(db, ingredient)
        ]
