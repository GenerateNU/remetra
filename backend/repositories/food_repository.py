import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models.food import Food
from schemas.food import FoodCreate


class FoodRepository:
    """
    Repository for handling database interactions related to food products.

    This is where all the actual database queries happen. Services call these methods
    to get data from the database, and then apply business logic on top of it.
    """

    def __init__(self):
        ## define db session here:
        self.largest_id = 0

    def create_unique_id(self):
        """Return a unique id for new Foods.

        Returns:
            unique_id (UUID): a unique id for a new Food.
        """
        self.largest_id += 1
        return UUID(int=self.largest_id)

    def create_food(self, db: Session, food: FoodCreate) -> Food:
        """
        Create a new food product in the database.

        Args:
            food_data: Validated data from FoodCreate model

        Returns:
            The created food with generated ID and timestamps
        """

        logging.info(f"Creating food in database: {food.name}")

        try:
            food_dict = food.model_dump()  # create a dict from the pydantic model
            db_food = Food(**food_dict)  # create a sqlalchemy model instance from the dict
            db.add(db_food)
            db.commit()
            db.refresh(db_food)
            return db_food
        except Exception as e:
            logging.error(f"Error creating food in database: {e}")
            db.rollback()
            raise e

    def delete_food_by_id(self, db: Session, food_id: UUID) -> Optional[Food] :
        """
        Delete a food product from the database by its ID.

        Args:
            food_id: The ID of the food to delete

        Returns:
            the food deleted, or None if not found
        """

        logging.info(f"Deleting food with ID {food_id} from database")

        food = self.get_food_by_id(db, food_id)
        if not food:
            logging.warning(f"Food with ID {food_id} not found for deletion")
            return None

        db.delete(food)
        db.commit()
        logging.info(f"Food with ID {food_id} successfully deleted")
        return food

    def get_food_by_id(self, db: Session, food_id: UUID) -> Optional[Food]:
        """
        Retrieve a food product from the database by its ID.

        Args:
            food_id: The ID of the food to retrieve
        Returns:
            The food with the specified ID, or None if not found
        """

        logging.info(f"Retrieving food with ID {food_id} from database")
        # get the food based on the id given
        return db.query(Food).filter(Food.id == food_id).first()

    def get_all_foods(self, db: Session) -> list[Food]:
        """
        Retrieve a list of all Food products in the database

        Returns:
            All of the foods in the database
        """
        logging.info("Retrieving all food from the database")
        return db.query(Food).all()

    def update_food_by_id(self, db: Session, food_id: UUID, food_data: FoodCreate) -> Optional[Food]:
        """
        Update a food product from the database by its ID.

        Args:
            food_id (UUID): The ID of the food to retrieve

        Returns:
            Food: the newly updated food with all fields, or None if not found
        """
        logging.info(f"Updating food with ID {food_id} in database")

        food_dict = food_data.model_dump()
        db.query(Food).filter(Food.id == food_id).update(food_dict)
        db.commit()
        food = db.query(Food).filter(Food.id == food_id).first()
        return food
