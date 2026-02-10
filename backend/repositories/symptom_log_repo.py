from uuid import UUID

import sqlalchemy as sa

from models.symptom_log import SymptomLog
from models.symptom_log_model import SymptomLogCreate


class SymptomLogRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get_by_id(self, log_id: UUID):
        query = sa.select(SymptomLog).where(SymptomLog.log_id == log_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, data, log: SymptomLog):
        log = SymptomLog(**data.model_dump())

        self.db_session.add(log)
        await self.db_session.commit()
        await self.db_session.refresh(log)
        return log

    async def delete(self, log_id: UUID) -> bool:
        query = sa.delete(SymptomLog).where(SymptomLog.log_id == log_id)
        result = await self.db_session.execute(query)
        await self.db_session.commit()
        return result.rowcount > 0
