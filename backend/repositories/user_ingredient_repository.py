from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from models.ingredient import Ingredient
from models.user_ingredient import IngredientPreference, UserIngredient


class UserIngredientRepository:
    def get_with_ingredients(self, db: Session, username: str):
        """Return (preference, Ingredient) pairs for every ingredient the user has categorized."""
        query = (
            sa.select(UserIngredient.preference, Ingredient)
            .join(Ingredient, Ingredient.id == UserIngredient.ingredient_id)
            .where(UserIngredient.username == username)
            .order_by(Ingredient.canonical_name)
        )
        return db.execute(query).all()

    def get_existing_ingredient_ids(self, db: Session, ingredient_ids: set[UUID]) -> set[UUID]:
        """Return which of the given IDs exist in the ingredients table."""
        if not ingredient_ids:
            return set()
        query = sa.select(Ingredient.id).where(Ingredient.id.in_(ingredient_ids))
        return set(db.execute(query).scalars().all())

    def replace_for_user(self, db: Session, username: str, preferences: dict[UUID, IngredientPreference]) -> None:
        """Delete the user's saved preferences and insert the new set, in one transaction."""
        try:
            db.execute(sa.delete(UserIngredient).where(UserIngredient.username == username))
            db.add_all(
                UserIngredient(username=username, ingredient_id=ingredient_id, preference=preference)
                for ingredient_id, preference in preferences.items()
            )
            db.commit()
        except Exception:
            db.rollback()
            raise