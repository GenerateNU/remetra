"""Authentication service for food CRUD."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from repositories.food_repository import FoodRepository
from schemas.food import FoodCreate, FoodResponse


class FoodService:
    """
    Service for handling food-related business logic.

    This is where all the interesting stuff happens - validation, calculations,
    business rules. Routes just call these methods and return the results.
    """

    def __init__(self):
        self.food_repo = FoodRepository()

    def create_food(self, db: Session, food_data: FoodCreate) -> FoodResponse:
        """
        Create a new food product with validation.

        Args:
            food_data: Validated data from FoodCreate model

        Returns:
            The created food with generated ID and timestamps

        Raises:
            ValueError: If validation fails
        """

        # do we still check duplicate names since a user can eat the same food/recipes multiple times
        created_food = self.food_repo.create_food(db, food_data)
        return FoodResponse.model_validate(created_food)

    def update_food_by_id(self, db: Session, food_id: UUID, food_data: FoodCreate) -> Optional[FoodResponse]:
        """
        Updates a food product in the database

        Args:
            food_id (int): the food ID to update
            food_data (dict): the new food_data
        Returns:

        """

        # check if the food exists first
        existing_food = self.food_repo.get_food_by_id(db, food_id)
        if not existing_food:
            return None

        updated_food = self.food_repo.update_food_by_id(db, food_id, food_data)

        return FoodResponse.model_validate(updated_food)

    def get_food_by_id(self, db: Session, food_id: UUID) -> Optional[FoodResponse]:
        """
        Retrieve a food by its ID.

        Args:
            food_id: The ID of the food to retrieve

        Returns:
            The food with the specified ID, or None if not found
        """
        food = self.food_repo.get_food_by_id(db, food_id)
        if not food:
            return None
        return FoodResponse.model_validate(food)

    def delete_food_by_id(self, db: Session, food_id: UUID) -> Optional[FoodResponse]:
        """
        Delete a food by its ID.

        Args:
            food_id: The ID of the food to delete

        Returns:
            The Food that was deleted, or None if not found
        """
        deleted_food = self.food_repo.delete_food_by_id(db, food_id)
        if not deleted_food:
            return None

        return FoodResponse.model_validate(deleted_food)

    def get_all_foods(self, db: Session) -> list[FoodResponse]:
        """
        Retrieve all food items.

        Returns:
            List of all food items
        """

        all_foods = self.food_repo.get_all_foods(db)
        new_list = list()
        for food in all_foods:
            new_list.append(FoodResponse.model_validate(food))
        return new_list
