"""Service tests for Food CRUD with real database."""

# import pytest
# from fastapi import HTTPException
import uuid

from schemas.food import FoodCreate
from services.food_service import FoodService


class TestFoodService:
    """Tests for FoodService"""

    def test_create_food_success(self, db_session, sample_food_data):
        """Tests successfuly Food creation"""
        service = FoodService()
        food_create = FoodCreate(**sample_food_data)
        food = service.create_food(db_session, food_create)

        assert food.id is not None
        assert food.name == "test pizza"
        assert food.ingredients == ["flour", "cheese", "tomato"]

    # The following test is commented out because I do not know how to test that something is already in the database
    def test_update_food_success(self, db_session, sample_food_data):
        """Test successfully updates Food"""
        service = FoodService()
        food_created = service.create_food(db_session, FoodCreate(**sample_food_data))

        # update the info
        new_ingredients = list(["flour", "cheese", "tomato", "pepperoni"])
        sample_food_update = {"name": sample_food_data["name"], 
                              "ingredients": list(new_ingredients), 
                              "username": sample_food_data["username"]}
        food_update = FoodCreate(**sample_food_update)

        food = service.update_food_by_id(db_session, food_created.id, food_update)

        assert food is not None
        assert food.ingredients == list(["flour", "cheese", "tomato", "pepperoni"])

    def test_update_food_not_there(self, db_session, sample_food_data):
        """Test updating a food that does not exist"""
        service = FoodService()
        food = service.update_food_by_id(db_session, uuid.UUID(int=0), sample_food_data)
        assert food is None

    def test_delete_food_success(self, db_session, sample_food_data):
        """Test successfully deletes Food"""
        service = FoodService()
        food_created = service.create_food(db_session, FoodCreate(**sample_food_data))
        food = service.delete_food_by_id(db_session, food_created.id)

        assert food is not None
        assert food.id == food_created.id

    def test_delete_food_not_there(self, db_session):
        """Test deleting a Food that is not in the database"""
        service = FoodService()
        food = service.delete_food_by_id(db_session, uuid.UUID(int=0))
        assert food is None

    def test_get_all_foods_success(self, db_session, multiple_foods_data):
        """Test get all foods"""
        service = FoodService()
        for food in multiple_foods_data:
            service.create_food(db_session, FoodCreate(**food))

        all_foods = service.get_all_foods(db_session)
        assert len(all_foods) == 3
        names = [food.name for food in all_foods]
        assert "test pizza" in names
        assert "test salad" in names
        assert "test sandwich" in names

    def test_get_food_success(self, db_session, sample_food_data):
        """Test get Food by id successful"""
        service = FoodService()
        food_created = service.create_food(db_session, FoodCreate(**sample_food_data))
        food = service.get_food_by_id(db_session, food_created.id)

        assert food is not None
        assert food.id == food_created.id

    def test_get_food_fail(self, db_session):
        """Test get Food by id failure"""
        service = FoodService()
        food = service.get_food_by_id(db_session, uuid.UUID(int=0))

        assert food is None
