import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models.food_log import FoodLog
from schemas.food_log import FoodLogCreate

logger = logging.getLogger(__name__)


class FoodLogRepository:
    """Repository for database interactions related to food logs."""

    def create_food_log(self, db: Session, food_log_data: FoodLogCreate) -> FoodLog:
        """Create a new food log entry."""
        logger.info("Creating food log for user: %s", food_log_data.username)
        try:
            food_log = FoodLog(**food_log_data.model_dump())
            db.add(food_log)
            db.commit()
            db.refresh(food_log)
            return food_log
        except Exception as e:
            db.rollback()
            logger.error("Error creating food log: %s", e)
            raise

    def get_food_log_by_id(self, db: Session, food_log_id: UUID) -> Optional[FoodLog]:
        """Retrieve a food log by its ID."""
        logger.info("Retrieving food log with ID %s", food_log_id)
        return db.query(FoodLog).filter(FoodLog.id == food_log_id).first()

    def get_food_logs_by_username(self, db: Session, username: str) -> list[FoodLog]:
        """Retrieve all food logs for a given user."""
        logger.info("Retrieving food logs for user: %s", username)
        return db.query(FoodLog).filter(FoodLog.username == username).all()

    def delete_food_log_by_id(self, db: Session, food_log_id: UUID) -> Optional[FoodLog]:
        """Delete a food log by its ID. Returns the deleted log or None if not found."""
        logger.info("Deleting food log with ID %s", food_log_id)
        food_log = self.get_food_log_by_id(db, food_log_id)
        if not food_log:
            return None
        try:
            db.delete(food_log)
            db.commit()
            return food_log
        except Exception as e:
            db.rollback()
            logger.error("Error deleting food log %s: %s", food_log_id, e)
            raise
