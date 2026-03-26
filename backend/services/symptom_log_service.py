from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from repositories.symptom_log_repository import SymptomLogRepository
from schemas.symptom_log import SymptomLogCreate, SymptomLogResponse


class SymptomLogService:
    """Business logic for symptom logs."""

    def __init__(self):
        self.repo = SymptomLogRepository()

    def get_symptom_log(self, db: Session, log_id: UUID) -> Optional[SymptomLogResponse]:
        log = self.repo.get_by_id(db, log_id)
        if not log:
            return None
        return SymptomLogResponse.model_validate(log)

    def create_symptom_log(self, db: Session, data: SymptomLogCreate) -> SymptomLogResponse:
        log = self.repo.create(db, data)
        return SymptomLogResponse.model_validate(log)

    def delete_symptom_log(self, db: Session, log_id: UUID) -> bool:
        return self.repo.delete(db, log_id)
