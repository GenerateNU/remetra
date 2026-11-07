import logging

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
        return [(slug, level) for slug, level in db.execute(query).all()]
