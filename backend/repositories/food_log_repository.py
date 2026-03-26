import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from schemas.food_log import FoodLogCreate, FoodLogResponse


class FoodLogService:
    """
    Service for handling food log business logic.
    """

    def __init__(self):
        self.food_log_repo = FoodLogRepository()

    def create_food_log(self, db: Session, food_log_data: FoodLogCreate) -> FoodLogResponse:
        """
        Create a new food log entry.

        Args:
            food_log_data: Validated data from FoodLogCreate model

        Returns:
            The created food log

        Raises:
            ValueError: If validation fails
        """
        logging.info(f"Creating food log for user: {food_log_data.username}")
        created_food_log = self.food_log_repo.create_food_log(db, food_log_data)
        return FoodLogResponse.model_validate(created_food_log)

    def get_food_log_by_id(self, db: Session, food_log_id: UUID) -> Optional[FoodLogResponse]:
        """
        Retrieve a food log by its ID.

        Args:
            food_log_id: The ID of the food log to retrieve

        Returns:
            The food log with the specified ID, or None if not found
        """
        food_log = self.food_log_repo.get_food_log_by_id(db, food_log_id)
        if not food_log:
            return None
        return FoodLogResponse.model_validate(food_log)

    def get_food_logs_by_username(self, db: Session, username: str) -> list[FoodLogResponse]:
        """
        Retrieve all food logs for a given user.

        Args:
            username: The username to retrieve food logs for

        Returns:
            List of food logs for the specified user
        """
        food_logs = self.food_log_repo.get_food_logs_by_username(db, username)
        return [FoodLogResponse.model_validate(log) for log in food_logs]

    def delete_food_log_by_id(self, db: Session, food_log_id: UUID) -> Optional[FoodLogResponse]:
        """
        Delete a food log by its ID.

        Args:
            food_log_id: The ID of the food log to delete

        Returns:
            The deleted food log, or None if not found
        """
        deleted_food_log = self.food_log_repo.delete_food_log_by_id(db, food_log_id)
        if not deleted_food_log:
            return None
        return FoodLogResponse.model_validate(deleted_food_log)