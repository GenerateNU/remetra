"""Integration tests for symptom repository."""

# import pytest
from repositories.symptom_repository import SymptomRepository
from schemas.symptom import SymptomCreate


class TestSymptomRepository:
    """integration tests for SymptomRepository."""

    def test_create_symptom(self, db_session, authenticated_user, sample_symptom_data):
        """Test creating a symptom product in the database."""
        # arrange
        repo = SymptomRepository()
        symptom = SymptomCreate(**sample_symptom_data)
        result = repo.create_symptom(db_session, symptom)

        assert result.id is not None
        assert result.name == sample_symptom_data["name"]
        assert result.location == sample_symptom_data["location"]
        assert result.sensation == sample_symptom_data["sensation"]

    def test_get_symptom_by_id(self, db_session, authenticated_user, sample_symptom_data):
        """Test retrieving a symptom product by ID."""
        repo = SymptomRepository()
        symptom = SymptomCreate(**sample_symptom_data)
        result = repo.create_symptom(db_session, symptom)

        result = repo.get_symptom_by_id(db_session, result.id)
        assert result is not None
        assert result.id is not None
        assert result.name == sample_symptom_data["name"]

    def test_get_all_symptoms(self, db_session, authenticated_user, multiple_symptoms_data):
        """Test retrieving all symptom products."""
        repo = SymptomRepository()
        for symptom_data in multiple_symptoms_data:
            symptom = SymptomCreate(**symptom_data)
            result = repo.create_symptom(db_session, symptom)

        result = repo.get_all_symptoms(db_session)

        assert len(result) == 3
        names = [symptom.name for symptom in result]
        assert "headache" in names
        assert "itchyelbow" in names
        assert "lala" in names

    def test_delete_symptom_by_id(self, db_session, authenticated_user, sample_symptom_data):
        """Test deleting a symptom product by ID."""
        repo = SymptomRepository()
        symptom = SymptomCreate(**sample_symptom_data)
        result = repo.create_symptom(db_session, symptom)

        deleted_symptom = repo.delete_symptom_by_id(db_session, result.id)
        assert deleted_symptom is not None
        assert deleted_symptom.id == result.id

        # try to get the deleted symptom
        result = repo.get_symptom_by_id(db_session, result.id)
        assert result is None

    def test_update_symptom_by_id(self, db_session, authenticated_user, sample_symptom_data):
        """Test updating a symptom product by ID."""
        repo = SymptomRepository()
        symptom = SymptomCreate(**sample_symptom_data)
        result = repo.create_symptom(db_session, symptom)

        updated_data = {
            "name": "rosycheeks",
            "location": "cheeks",
            "sensation": "burning",
        }
        updated_symptom = repo.update_symptom_by_id(db_session, result.id, updated_data)
        assert updated_symptom is not None
        assert updated_symptom.id == result.id
        assert updated_symptom.name == updated_data["name"]
        assert updated_symptom.location == updated_data["location"]
        assert updated_symptom.sensation == updated_data["sensation"]
