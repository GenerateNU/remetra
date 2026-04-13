import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models.symptom import Symptom
from schemas.symptom import SymptomCreate


class SymptomRepository:
    """
    Repository for handling database interactions related to symptoms.

    This is where all the actual database queries happen. Services call these methods
    to get data from the database, and then apply business logic on top of it.
    """

    def __init__(self):
        # No local state needed for DB-driven IDs
        pass

    def create_symptom(self, db: Session, symptom: SymptomCreate) -> Symptom:
        """
        Create a new symptom in the database.

        Args:
            symptom: Validated data from SymptomCreate model

        Returns:
            The created symptom with generated ID and timestamps
        """

        logging.info(f"Creating symptom in database: {symptom.name}")

        try:
            symptom_dict = symptom.model_dump()
            db_symptom = Symptom(**symptom_dict)

            db.add(db_symptom)
            db.commit()
            db.refresh(db_symptom)

            return db_symptom

        except Exception as e:
            logging.error(f"Error creating symptom in database: {e}")
            db.rollback()
            raise e

    def get_symptom_by_id(self, db: Session, symptom_id: UUID) -> Optional[Symptom]:
        """
        Retrieve a symptom from the database by its ID.
        """

        logging.info(f"Retrieving symptom with ID {symptom_id} from database")

        return db.query(Symptom).filter(Symptom.id == symptom_id).first()

    def get_all_symptoms(self, db: Session, username: Optional[str] = None) -> list[Symptom]:
        """
        Retrieve all symptoms from the database, optionally filtered by username.
        """

        logging.info(f"Retrieving all symptoms from database (username={username})")

        query = db.query(Symptom)
        if username:
            query = query.filter(Symptom.username == username)
        return query.all()

    def update_symptom_by_id(
        self,
        db: Session,
        symptom_id: UUID,
        symptom_data: dict,
    ) -> Optional[Symptom]:
        """
        Update a symptom in the database by its ID.
        """

        logging.info(f"Updating symptom with ID {symptom_id}")

        symptom = db.query(Symptom).filter(Symptom.id == symptom_id)

        if not symptom.first():
            logging.warning(f"Symptom with ID {symptom_id} not found for update")
            return None

        symptom.update(symptom_data)
        db.commit()

        updated = db.query(Symptom).filter(Symptom.id == symptom_id).first()
        return updated

    def delete_symptom_by_id(
        self,
        db: Session,
        symptom_id: UUID,
    ) -> Optional[Symptom]:
        """
        Delete a symptom from the database by its ID.
        """

        logging.info(f"Deleting symptom with ID {symptom_id}")

        symptom = self.get_symptom_by_id(db, symptom_id)

        if not symptom:
            logging.warning(f"Symptom with ID {symptom_id} not found for deletion")
            return None

        db.delete(symptom)
        db.commit()

        logging.info(f"Symptom with ID {symptom_id} successfully deleted")
        return symptom
