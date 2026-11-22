from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session, joinedload

from models.symptom_log import SymptomLog


class SymptomLogRepository:
    def get_by_id(self, db: Session, log_id: UUID):
        query = sa.select(SymptomLog).options(joinedload(SymptomLog.symptom)).where(SymptomLog.id == log_id)
        result = db.execute(query)
        return result.unique().scalar_one_or_none()

    def create(self, db: Session, data):
        log = SymptomLog(**data.model_dump())
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    def get_by_username(self, db: Session, username: str):
        query = sa.select(SymptomLog).options(joinedload(SymptomLog.symptom)).where(SymptomLog.username == username)
        result = db.execute(query)
        return result.unique().scalars().all()

    def get_by_username_between(self, db: Session, username: str, start: datetime, end: datetime):
        """Logs for a user with start <= timestamp <= end, oldest first, each with its symptom loaded."""
        query = (
            sa.select(SymptomLog)
            .options(joinedload(SymptomLog.symptom))
            .where(
                SymptomLog.username == username,
                SymptomLog.timestamp >= start,
                SymptomLog.timestamp <= end,
            )
            .order_by(SymptomLog.timestamp.asc())
        )
        result = db.execute(query)
        return result.unique().scalars().all()

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
        log = self.get_by_id(db, log_id)
        if not log:
            return False
        db.delete(log)
        db.commit()
        return True
