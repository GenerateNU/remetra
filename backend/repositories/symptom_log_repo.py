import sqlalchemy as sa

from models.symptom_log_model import SymptomLog


class SymptomLogRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get_by_id(self, log_id: int):
        query = sa.select(SymptomLog).where(SymptomLog.log_id == log_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, log: SymptomLog):
        self.db_session.add(log)
        await self.db_session.commit()
        await self.db_session.refresh(log)
        return log

    async def delete(self, log_id: int) -> bool:
        query = sa.delete(SymptomLog).where(SymptomLog.log_id == log_id)
        result = await self.db_session.execute(query)
        await self.db_session.commit()
        return result.rowcount > 0
