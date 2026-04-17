"""Authentication service for symptom CRUD."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from repositories.symptom_repository import SymptomRepository
from schemas.symptom import SymptomCreate, SymptomResponse


class SymptomService:
    """
    Service for handling symptom-related business logic.

    This is where all the interesting stuff happens - validation, calculations,
    business rules. Routes just call these methods and return the results.
    """

    def __init__(self):
        self.symptom_repo = SymptomRepository()

    def create_symptom(self, db: Session, symptom_data: SymptomCreate) -> SymptomResponse:
        """
        Create a new symptom with validation.

        Args:
            symptom_data: Validated data from SymptomCreate model

        Returns:
            The created symptom with generated ID and timestamps

        Raises:
            ValueError: If validation fails
        """
        created_symptom = self.symptom_repo.create_symptom(db, symptom_data)
        return SymptomResponse.model_validate(created_symptom)

    def update_symptom_by_id(self, db: Session, symptom_id: UUID, symptom_data: dict) -> Optional[SymptomResponse]:
        """
        Updates a symptom in the database

        Args:
            symptom_id (int): the symptom ID to update
            symptom_data (dict): the new symptom_data
        Returns:

        """

        # check if the symptom exists first
        exisiting_symptom = self.symptom_repo.get_symptom_by_id(db, symptom_id)
        if not exisiting_symptom:
            return None

        updated_symptom = self.symptom_repo.update_symptom_by_id(db, symptom_id, symptom_data)

        return SymptomResponse.model_validate(updated_symptom)

    def get_symptom_by_id(self, db: Session, symptom_id: UUID) -> Optional[SymptomResponse]:
        """
        Retrieve a symptom by its ID.

        Args:
            symptom_id: The ID of the symptom to retrieve

        Returns:
            The symptom with the specified ID, or None if not found
        """
        symptom = self.symptom_repo.get_symptom_by_id(db, symptom_id)
        if not symptom:
            return None
        return SymptomResponse.model_validate(symptom)

    def delete_symptom_by_id(self, db: Session, symptom_id: UUID) -> Optional[SymptomResponse]:
        """
        Delete a symptom by its ID.

        Args:
            symptom_id: The ID of the symptom to delete

        Returns:
            The symptom that was deleted, or None if not found
        """
        deleted_symptom = self.symptom_repo.delete_symptom_by_id(db, symptom_id)
        if not deleted_symptom:
            return None

        return SymptomResponse.model_validate(deleted_symptom)

    def get_all_symptoms(self, db: Session, username: Optional[str] = None) -> list[SymptomResponse]:
        """
        Retrieve all symptom items, optionally filtered by username.

        Returns:
            List of all symptom items (filtered by username if provided)
        """

        all_symptoms = self.symptom_repo.get_all_symptoms(db, username=username)
        new_list = list()
        for symptom in all_symptoms:
            new_list.append(SymptomResponse.model_validate(symptom))
        return new_list
