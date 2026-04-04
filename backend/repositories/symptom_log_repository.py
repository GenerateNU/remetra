from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from models.symptom_log import SymptomLog


class SymptomLogRepository:
    def get_by_id(self, db: Session, log_id: UUID):
        query = sa.select(SymptomLog).where(SymptomLog.id == log_id)
        result = db.execute(query)
        return result.scalar_one_or_none()

    def create(self, db: Session, data):
        log = SymptomLog(**data.model_dump())
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    def get_by_username(self, db: Session, username: str):
        query = sa.select(SymptomLog).where(SymptomLog.username == username)
        result = db.execute(query)
        return result.scalars().all()

    def update(self, db: Session, log_id: UUID, data):
        log = self.get_by_id(db, log_id)
        if not log:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(log, field, value)
        db.commit()
        db.refresh(log)
        return log

    def delete(self, db: Session, log_id: UUID) -> bool:
        query = sa.delete(SymptomLog).where(SymptomLog.id == log_id)
        result = db.execute(query)
        db.commit()
        return result.rowcount > 0
