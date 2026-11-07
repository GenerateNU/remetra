"""Database access for stored daily ingredient pools."""

import logging
from datetime import date

from sqlalchemy.orm import Session

from models.ingredient_pool import IngredientPool

logger = logging.getLogger(__name__)


class IngredientPoolRepository:
    """Reads and writes ingredient_pools rows."""

    def get_by_user_and_date(
        self,
        db: Session,
        username: str,
        pool_date: date,
    ) -> IngredientPool | None:
        """Return the pool for this user and date, or None if it has not been created."""
        return (
            db.query(IngredientPool)
            .filter(
                IngredientPool.username == username,
                IngredientPool.pool_date == pool_date,
            )
            .first()
        )

    def create(
        self,
        db: Session,
        username: str,
        pool_date: date,
        ingredient_ids: list[str],
        washout: bool,
    ) -> IngredientPool:
        """
        Insert a new pool row.

        Raises:
            IntegrityError: If the user already has a pool for `pool_date`.
        """
        ingredient_pool = IngredientPool(
            username=username,
            pool_date=pool_date,
            ingredient_ids=ingredient_ids,
            washout=washout,
        )
        try:
            db.add(ingredient_pool)
            db.commit()
            db.refresh(ingredient_pool)
            return ingredient_pool
        except Exception as e:
            db.rollback()
            logger.error("Failed to create IngredientPool: %s", e)
            raise
