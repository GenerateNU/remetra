import logging
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from models.component import Component
from models.ingredient import Ingredient
from models.ingredient_component import IngredientComponent


class TaxonomyRepository:
    """Read access to the ingredient/component taxonomy tables."""

    def get_components_for_ingredient(self, db: Session, ingredient: str) -> list[tuple[str, int]]:
        """Return (component slug, concentration_level) pairs for an ingredient.

        Matches the ingredient's slug or canonical_name, case-insensitively. Results are ordered by component slug.
        """
        logging.info(f"Retrieving components for ingredient {ingredient!r} from database")
        key = ingredient.strip().lower()
        query = (
            sa.select(Component.slug, IngredientComponent.concentration_level)
            .join(IngredientComponent, IngredientComponent.component_id == Component.id)
            .join(Ingredient, IngredientComponent.ingredient_id == Ingredient.id)
            .where(sa.or_(sa.func.lower(Ingredient.slug) == key, sa.func.lower(Ingredient.canonical_name) == key))
            .order_by(Component.slug)
        )
        return [(slug, concentration_level) for slug, concentration_level in db.execute(query).all()]

    def get_components_for_ingredient_id(self, db: Session, ingredient_id: UUID) -> list[tuple[UUID, int]] | None:
        """Return (component_id, concentration_level) pairs for an ingredient, ordered by component_id.

        Returns None if the ingredient doesn't exist, and [] if it exists but has no components.
        Level-0 components are included; callers decide whether to skip them.
        """
        logging.info(f"Retrieving components for ingredient id {ingredient_id} from database")
        if db.get(Ingredient, ingredient_id) is None:
            return None
        query = (
            sa.select(IngredientComponent.component_id, IngredientComponent.concentration_level)
            .where(IngredientComponent.ingredient_id == ingredient_id)
            .order_by(IngredientComponent.component_id)
        )
        return [(component_id, concentration_level) for component_id, concentration_level in db.execute(query).all()]
