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
        return [(slug, level) for slug, level in db.execute(query).all()]

    def ingredient_ids_for(
        self,
        db: Session,
        *,
        component_slugs: set[str],
        ingredient_slugs: set[str],
    ) -> set[UUID]:
        """Ingredient ids that match any of the component slugs or ingredient slugs."""
        ids: set[UUID] = set()
        if ingredient_slugs:
            query = sa.select(Ingredient.id).where(Ingredient.slug.in_(ingredient_slugs))
            ids.update(db.execute(query).scalars().all())
        if component_slugs:
            query = (
                sa.select(Ingredient.id)
                .join(IngredientComponent, IngredientComponent.ingredient_id == Ingredient.id)
                .join(Component, Component.id == IngredientComponent.component_id)
                .where(Component.slug.in_(component_slugs))
            )
            ids.update(db.execute(query).scalars().all())
        return ids
