"""Integration tests for FoodLogRepository and FoodLogService."""

from datetime import datetime
from uuid import uuid4

import pytest

from repositories.food_log_repository import FoodLogRepository
from schemas.food_log import FoodLogCreate, FoodLogResponse, FoodLogUpdate
from services.food_log_service import FoodLogService


@pytest.fixture
def sample_food_log_data(authenticated_user, created_food):
    """FoodLogCreate with real FK-valid username and food_id."""
    return FoodLogCreate(
        username=authenticated_user["username"],
        food_id=created_food.id,
        timestamp=datetime(2025, 3, 1, 12, 0),
        quantity="1 serving",
        notes="Test food log entry",
    )


class TestFoodLogRepository:
    """Integration tests for FoodLogRepository."""

    def test_create_food_log(self, db_session, sample_food_log_data):
        """Creating a food log returns a FoodLog ORM object with all fields populated."""
        repo = FoodLogRepository()

        result = repo.create_food_log(db_session, sample_food_log_data)

        assert result.id is not None
        assert result.username == sample_food_log_data.username
        assert result.food_id == sample_food_log_data.food_id
        assert result.quantity == sample_food_log_data.quantity
        assert result.notes == sample_food_log_data.notes
        assert result.created_at is not None

    def test_get_food_log_by_id(self, db_session, sample_food_log_data):
        """Retrieving a food log by ID returns the correct row."""
        repo = FoodLogRepository()
        created = repo.create_food_log(db_session, sample_food_log_data)

        result = repo.get_food_log_by_id(db_session, created.id)

        assert result is not None
        assert result.id == created.id
        assert result.username == sample_food_log_data.username

    def test_get_food_log_by_id_not_found(self, db_session):
        """get_food_log_by_id returns None for a non-existent ID."""
        repo = FoodLogRepository()

        result = repo.get_food_log_by_id(db_session, uuid4())

        assert result is None

    def test_get_food_logs_by_username(self, db_session, authenticated_user, created_food):
        """get_food_logs_by_username returns all logs for a given user."""
        repo = FoodLogRepository()
        username = authenticated_user["username"]

        for i in range(3):
            data = FoodLogCreate(
                username=username,
                food_id=created_food.id,
                timestamp=datetime(2025, 3, i + 1, 12, 0),
            )
            repo.create_food_log(db_session, data)

        results = repo.get_food_logs_by_username(db_session, username)

        assert len(results) == 3
        assert all(r.username == username for r in results)

    def test_get_food_logs_by_username_empty(self, db_session):
        """get_food_logs_by_username returns an empty list for a user with no logs."""
        repo = FoodLogRepository()

        results = repo.get_food_logs_by_username(db_session, "no_such_user")

        assert results == []

    def test_delete_food_log_by_id(self, db_session, sample_food_log_data):
        """Deleting a food log returns the deleted row and removes it from the DB."""
        repo = FoodLogRepository()
        created = repo.create_food_log(db_session, sample_food_log_data)

        deleted = repo.delete_food_log_by_id(db_session, created.id)

        assert deleted is not None
        assert deleted.id == created.id
        assert repo.get_food_log_by_id(db_session, created.id) is None

    def test_delete_food_log_by_id_not_found(self, db_session):
        """Deleting a non-existent food log returns None."""
        repo = FoodLogRepository()

        result = repo.delete_food_log_by_id(db_session, uuid4())

        assert result is None


class TestFoodLogService:
    """Integration tests for FoodLogService."""

    def test_create_food_log(self, db_session, sample_food_log_data):
        """create_food_log returns a FoodLogResponse with correct fields."""
        service = FoodLogService()

        result = service.create_food_log(db_session, sample_food_log_data)

        assert isinstance(result, FoodLogResponse)
        assert result.id is not None
        assert result.username == sample_food_log_data.username
        assert result.food_id == sample_food_log_data.food_id
        assert result.quantity == sample_food_log_data.quantity
        assert result.created_at is not None

    def test_get_food_log_by_id(self, db_session, sample_food_log_data):
        """get_food_log_by_id returns a FoodLogResponse for a known ID."""
        service = FoodLogService()
        created = service.create_food_log(db_session, sample_food_log_data)

        result = service.get_food_log_by_id(db_session, created.id)

        assert isinstance(result, FoodLogResponse)
        assert result.id == created.id

    def test_get_food_log_by_id_not_found(self, db_session):
        """get_food_log_by_id returns None for a non-existent ID."""
        service = FoodLogService()

        result = service.get_food_log_by_id(db_session, uuid4())

        assert result is None

    def test_get_food_logs_by_username(self, db_session, authenticated_user, created_food):
        """get_food_logs_by_username returns all FoodLogResponses for the user."""
        service = FoodLogService()
        username = authenticated_user["username"]

        for i in range(2):
            data = FoodLogCreate(
                username=username,
                food_id=created_food.id,
                timestamp=datetime(2025, 3, i + 1, 12, 0),
            )
            service.create_food_log(db_session, data)

        results = service.get_food_logs_by_username(db_session, username)

        assert len(results) == 2
        assert all(isinstance(r, FoodLogResponse) for r in results)
        assert all(r.username == username for r in results)

    def test_get_food_logs_by_username_empty(self, db_session):
        """get_food_logs_by_username returns an empty list for a user with no logs."""
        service = FoodLogService()

        results = service.get_food_logs_by_username(db_session, "no_such_user")

        assert results == []

    def test_delete_food_log_by_id(self, db_session, sample_food_log_data):
        """delete_food_log_by_id returns the deleted FoodLogResponse and removes it."""
        service = FoodLogService()
        created = service.create_food_log(db_session, sample_food_log_data)

        deleted = service.delete_food_log_by_id(db_session, created.id)

        assert isinstance(deleted, FoodLogResponse)
        assert deleted.id == created.id
        assert service.get_food_log_by_id(db_session, created.id) is None

    def test_delete_food_log_by_id_not_found(self, db_session):
        """delete_food_log_by_id returns None for a non-existent log."""
        service = FoodLogService()

        result = service.delete_food_log_by_id(db_session, uuid4())

        assert result is None

    def test_update_food_log(self, db_session, sample_food_log_data):
        """update_food_log returns an updated FoodLogResponse."""
        service = FoodLogService()
        created = service.create_food_log(db_session, sample_food_log_data)

        result = service.update_food_log(db_session, created.id, FoodLogUpdate(notes="updated notes"))

        assert isinstance(result, FoodLogResponse)
        assert result.id == created.id
        assert result.notes == "updated notes"

    def test_update_food_log_not_found(self, db_session):
        """update_food_log returns None for a non-existent log."""
        service = FoodLogService()

        result = service.update_food_log(db_session, uuid4(), FoodLogUpdate(notes="x"))

        assert result is None
