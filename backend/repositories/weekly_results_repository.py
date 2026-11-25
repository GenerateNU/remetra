"""Read-only queries behind the weekly results: the ingredient map and a user's settled meals."""

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Session

from models.component import Component
from models.food import Food
from models.food_log import FoodLog
from models.ingredient import Ingredient
from models.ingredient_component import IngredientComponent


class WeeklyResultsRepository:
    def get_ingredient_levels(self, db: Session) -> dict[str, dict[str, int]]:
        """Map every lowercased ingredient slug, canonical name and alias to {component slug: concentration level}.

        Level-0 mappings are left out.
        """
        query = (
            sa.select(
                Ingredient.slug,
                Ingredient.canonical_name,
                Ingredient.aliases,
                Component.slug,
                IngredientComponent.concentration_level,
            )
            .join(IngredientComponent, IngredientComponent.ingredient_id == Ingredient.id)
            .join(Component, IngredientComponent.component_id == Component.id)
            .where(IngredientComponent.concentration_level > 0)
        )
        levels: dict[str, dict[str, int]] = {}
        for slug, canonical_name, aliases, component_slug, level in db.execute(query).all():
            names = [slug, canonical_name, *(aliases or [])]
            for name in names:
                if isinstance(name, str) and name.strip():
                    levels.setdefault(name.strip().lower(), {})[component_slug] = level
        return levels

    def get_meal_ingredients(self, db: Session, username: str, eaten_before: datetime) -> list[list[str]]:
        """Return the ingredient list of each of the user's food logs eaten at or before `eaten_before`."""
        query = (
            sa.select(Food.ingredients)
            .join(FoodLog, FoodLog.food_id == Food.id)
            .where(FoodLog.username == username, FoodLog.timestamp <= eaten_before)
        )
        return [ingredients or [] for ingredients in db.execute(query).scalars().all()]

    def get_first_meal_time(self, db: Session, username: str) -> datetime | None:
        """Return when the user's earliest food log was eaten, or None if they have none."""
        query = sa.select(sa.func.min(FoodLog.timestamp)).where(FoodLog.username == username)
        return db.execute(query).scalar_one_or_none()
