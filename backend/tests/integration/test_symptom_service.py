"""Service tests for Symptom CRUD with real database."""

import uuid

from schemas.symptom import SymptomCreate
from services.symptom_service import SymptomService


class TestSymptomService:
    """Tests for SymptomService"""

    def test_create_symptom_success(self, db_session, authenticated_user, sample_symptom_data):
        """Test successful symptom creation."""
        service = SymptomService()
        symptom_create = SymptomCreate(**sample_symptom_data)
        symptom = service.create_symptom(db_session, symptom_create)

        assert symptom.id is not None
        assert symptom.name == sample_symptom_data["name"]
        assert symptom.location == sample_symptom_data["location"]
        assert symptom.sensation == sample_symptom_data["sensation"]

    def test_update_symptom_success(self, db_session, authenticated_user, sample_symptom_data):
        """Test successfully updates symptom."""
        service = SymptomService()
        symptom_created = service.create_symptom(db_session, SymptomCreate(**sample_symptom_data))

        updated_data = {
            "name": "rosycheeks",
            "location": "cheeks",
            "sensation": "burning",
            "username": sample_symptom_data["username"],
        }
        symptom = service.update_symptom_by_id(db_session, symptom_created.id, updated_data)

        assert symptom is not None
        assert symptom.name == "rosycheeks"
        assert symptom.location == "cheeks"
        assert symptom.sensation == "burning"

    def test_update_symptom_not_there(self, db_session, authenticated_user, sample_symptom_data):
        """Test updating a symptom that does not exist."""
        service = SymptomService()
        symptom = service.update_symptom_by_id(db_session, uuid.UUID(int=0), sample_symptom_data)
        assert symptom is None

    def test_delete_symptom_success(self, db_session, authenticated_user, sample_symptom_data):
        """Test successfully deletes symptom."""
        service = SymptomService()
        symptom_created = service.create_symptom(db_session, SymptomCreate(**sample_symptom_data))
        symptom = service.delete_symptom_by_id(db_session, symptom_created.id)

        assert symptom is not None
        assert symptom.id == symptom_created.id

    def test_delete_symptom_not_there(self, db_session):
        """Test deleting a symptom that is not in the database."""
        service = SymptomService()
        symptom = service.delete_symptom_by_id(db_session, uuid.UUID(int=0))
        assert symptom is None

    def test_get_all_symptoms_success(self, db_session, authenticated_user, multiple_symptoms_data):
        """Test get all symptoms."""
        service = SymptomService()
        for data in multiple_symptoms_data:
            service.create_symptom(db_session, SymptomCreate(**data))

        all_symptoms = service.get_all_symptoms(db_session)
        assert len(all_symptoms) == 3
        names = [s.name for s in all_symptoms]
        assert "headache" in names
        assert "itchyelbow" in names
        assert "lala" in names

    def test_get_symptom_success(self, db_session, authenticated_user, sample_symptom_data):
        """Test get symptom by id successful."""
        service = SymptomService()
        symptom_created = service.create_symptom(db_session, SymptomCreate(**sample_symptom_data))
        symptom = service.get_symptom_by_id(db_session, symptom_created.id)

        assert symptom is not None
        assert symptom.id == symptom_created.id

    def test_get_symptom_fail(self, db_session):
        """Test get symptom by id failure."""
        service = SymptomService()
        symptom = service.get_symptom_by_id(db_session, uuid.UUID(int=0))

        assert symptom is None
