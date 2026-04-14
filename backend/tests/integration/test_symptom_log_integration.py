"""Integration tests for symptom log repository and service with real database."""

from datetime import datetime

import pytest

from repositories.symptom_log_repository import SymptomLogRepository
from repositories.symptom_repository import SymptomRepository
from schemas.symptom import SymptomCreate
from schemas.symptom_log import SymptomLogCreate, SymptomLogUpdate
from services.symptom_log_service import SymptomLogService


@pytest.fixture
def created_symptom(db_session, authenticated_user, sample_symptom_data):
    """Create a symptom in the DB and return it (needed for FK in symptom logs)."""
    repo = SymptomRepository()
    symptom = SymptomCreate(**sample_symptom_data)
    return repo.create_symptom(db_session, symptom)


@pytest.fixture
def sample_log_data(authenticated_user, created_symptom):
    """Sample symptom log creation data using real user and symptom IDs."""
    return SymptomLogCreate(
        username=authenticated_user["username"],
        symptom_id=created_symptom.id,
        intensity=5,
        timestamp=datetime(2025, 1, 15, 10, 30),
        duration=60,
        notes="Mild headache after lunch",
    )


class TestSymptomLogRepository:
    """Integration tests for SymptomLogRepository."""

    def test_create_symptom_log(self, db_session, sample_log_data):
        """Test creating a symptom log in the database."""
        repo = SymptomLogRepository()
        created = repo.create(db_session, sample_log_data)

        db_session.expire_all()
        result = repo.get_by_id(db_session, created.id)

        assert result is not None
        assert result.id == created.id
        assert result.username == sample_log_data.username
        assert result.symptom_id == sample_log_data.symptom_id
        assert result.intensity == sample_log_data.intensity
        assert result.duration == sample_log_data.duration
        assert result.notes == sample_log_data.notes
        assert result.created_at is not None

    def test_get_symptom_log_by_id(self, db_session, sample_log_data):
        """Test retrieving a symptom log by ID."""
        repo = SymptomLogRepository()
        created = repo.create(db_session, sample_log_data)

        result = repo.get_by_id(db_session, created.id)
        assert result is not None
        assert result.id == created.id
        assert result.intensity == sample_log_data.intensity

    def test_get_symptom_log_not_found(self, db_session):
        """Test that get_by_id returns None for a non-existent log."""
        from uuid import uuid4

        repo = SymptomLogRepository()
        result = repo.get_by_id(db_session, uuid4())
        assert result is None

    def test_delete_symptom_log(self, db_session, sample_log_data):
        """Test deleting a symptom log."""
        repo = SymptomLogRepository()
        created = repo.create(db_session, sample_log_data)

        deleted = repo.delete(db_session, created.id)
        assert deleted is True

        result = repo.get_by_id(db_session, created.id)
        assert result is None

    def test_delete_symptom_log_not_found(self, db_session):
        """Test that deleting a non-existent log returns False."""
        from uuid import uuid4

        repo = SymptomLogRepository()
        result = repo.delete(db_session, uuid4())
        assert result is False


class TestSymptomLogService:
    """Integration tests for SymptomLogService."""

    def test_create_symptom_log(self, db_session, sample_log_data):
        """Test creating a symptom log via the service."""
        service = SymptomLogService()
        created = service.create_symptom_log(db_session, sample_log_data)

        db_session.expire_all()
        result = service.get_symptom_log(db_session, created.id)

        assert result is not None
        assert result.id == created.id
        assert result.username == sample_log_data.username
        assert result.intensity == sample_log_data.intensity
        assert result.created_at is not None

    def test_get_symptom_log(self, db_session, sample_log_data):
        """Test retrieving a symptom log via the service."""
        service = SymptomLogService()
        created = service.create_symptom_log(db_session, sample_log_data)

        result = service.get_symptom_log(db_session, created.id)
        assert result is not None
        assert result.id == created.id
        assert result.intensity == sample_log_data.intensity

    def test_get_symptom_log_not_found(self, db_session):
        """Test that getting a non-existent log returns None."""
        from uuid import uuid4

        service = SymptomLogService()
        result = service.get_symptom_log(db_session, uuid4())
        assert result is None

    def test_delete_symptom_log(self, db_session, sample_log_data):
        """Test deleting a symptom log via the service."""
        service = SymptomLogService()
        created = service.create_symptom_log(db_session, sample_log_data)

        deleted = service.delete_symptom_log(db_session, created.id)
        assert deleted is True

        result = service.get_symptom_log(db_session, created.id)
        assert result is None

    def test_delete_symptom_log_not_found(self, db_session):
        """Test that deleting a non-existent log returns False."""
        from uuid import uuid4

        service = SymptomLogService()
        result = service.delete_symptom_log(db_session, uuid4())
        assert result is False

    def test_get_symptom_logs_by_username(self, db_session, sample_log_data):
        """get_symptom_logs_by_username returns all logs for the user."""
        from schemas.symptom_log import SymptomLogResponse

        service = SymptomLogService()
        service.create_symptom_log(db_session, sample_log_data)
        service.create_symptom_log(db_session, sample_log_data)

        results = service.get_symptom_logs_by_username(db_session, sample_log_data.username)

        assert len(results) == 2
        assert all(isinstance(r, SymptomLogResponse) for r in results)
        assert all(r.username == sample_log_data.username for r in results)

    def test_update_symptom_log(self, db_session, sample_log_data):
        """update_symptom_log returns an updated SymptomLogResponse."""
        from schemas.symptom_log import SymptomLogResponse

        service = SymptomLogService()
        created = service.create_symptom_log(db_session, sample_log_data)

        result = service.update_symptom_log(db_session, created.id, SymptomLogUpdate(intensity=9))

        assert isinstance(result, SymptomLogResponse)
        assert result.id == created.id
        assert result.intensity == 9

    def test_update_symptom_log_not_found(self, db_session):
        """update_symptom_log returns None for a non-existent log."""
        from uuid import uuid4

        service = SymptomLogService()
        result = service.update_symptom_log(db_session, uuid4(), SymptomLogUpdate(intensity=5))
        assert result is None
