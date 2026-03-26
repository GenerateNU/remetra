"""Service layer for food log business logic."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from repositories.food_log_repository import FoodLogRepository
from schemas.food_log import FoodLogCreate, FoodLogResponse


class FoodLogService:
    """Service for handling food log business logic."""

    def __init__(self):
        self.food_log_repo = FoodLogRepository()

    def create_food_log(self, db: Session, food_log_data: FoodLogCreate) -> FoodLogResponse:
        logging.info(f"Creating food log for user: {food_log_data.username}")
        created = self.food_log_repo.create_food_log(db, food_log_data)
        return FoodLogResponse.model_validate(created)

    def get_food_log_by_id(self, db: Session, food_log_id: UUID) -> Optional[FoodLogResponse]:
        food_log = self.food_log_repo.get_food_log_by_id(db, food_log_id)
        if not food_log:
            return None
        return FoodLogResponse.model_validate(food_log)

    def get_food_logs_by_username(self, db: Session, username: str) -> list[FoodLogResponse]:
        food_logs = self.food_log_repo.get_food_logs_by_username(db, username)
        return [FoodLogResponse.model_validate(log) for log in food_logs]

    def delete_food_log_by_id(self, db: Session, food_log_id: UUID) -> Optional[FoodLogResponse]:
        deleted = self.food_log_repo.delete_food_log_by_id(db, food_log_id)
        if not deleted:
            return None
        return FoodLogResponse.model_validate(deleted)