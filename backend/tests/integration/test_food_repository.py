"""Integration tests for food repository."""

# import pytest
from repositories.food_repository import FoodRepository
from schemas.food import FoodCreate


class TestFoodRepository:
    """integration tests for FoodRepository."""

    def test_create_food(self, db_session, sample_food_data):
        """Test creating a food product in the database."""
        # arrange
        repo = FoodRepository()
        food = FoodCreate(**sample_food_data)
        result = repo.create_food(db_session, food)

        assert result.id is not None
        assert result.name == sample_food_data["name"]
        assert result.ingredients == sample_food_data["ingredients"]

    def test_get_food_by_id(self, db_session, sample_food_data):
        """Test retrieving a food product by ID."""
        repo = FoodRepository()
        food = FoodCreate(**sample_food_data)
        result = repo.create_food(db_session, food)

        result = repo.get_food_by_id(db_session, result.id)
        assert result is not None
        assert result.id is not None
        assert result.name == sample_food_data["name"]

    def test_get_all_foods(self, db_session, multiple_foods_data):
        """Test retrieving all food products."""
        repo = FoodRepository()
        for food_data in multiple_foods_data:
            food = FoodCreate(**food_data)
            result = repo.create_food(db_session, food)

        result = repo.get_all_foods(db_session)

        assert len(result) == 3
        names = [food.name for food in result]
        assert "test pizza" in names
        assert "test salad" in names
        assert "test sandwich" in names

    def test_delete_food_by_id(self, db_session, sample_food_data):
        """Test deleting a food product by ID."""
        repo = FoodRepository()
        food = FoodCreate(**sample_food_data)
        result = repo.create_food(db_session, food)

        deleted_food = repo.delete_food_by_id(db_session, result.id)
        assert deleted_food is not None
        assert deleted_food.id == result.id

        # try to get the deleted food
        result = repo.get_food_by_id(db_session, result.id)
        assert result is None

    def test_update_food_by_id(self, db_session, sample_food_data):
        """Test updating a food product by ID."""
        repo = FoodRepository()
        food = FoodCreate(**sample_food_data)
        result = repo.create_food(db_session, food)

        updated_data = {
            "name": "updated pizza",
            "ingredients": ["flour", "cheese", "tomato", "pepperoni"],
        }
        updated_food = repo.update_food_by_id(db_session, result.id, FoodCreate(**updated_data))
        assert updated_food is not None
        assert updated_food.id == result.id
        assert updated_food.name == updated_data["name"]
        assert updated_food.ingredients == updated_data["ingredients"]
