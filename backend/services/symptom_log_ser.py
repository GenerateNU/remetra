from datetime import datetime, timezone
from decimal import Decimal
import sqlalchemy as sa
from models.symptom_log_model import symptom_log

class SymptomLogService:  
    """SQLAlchemy model for symptom logs."""
    def __init__(self, db_session):
        self.db_session = db_session

    async def get_symptom_log(self, log_id: int) -> symptom_log | None:
        """Fetch a symptom log by its ID."""
        query = sa.select(symptom_log).where(symptom_log.log_id == log_id)
        result = await self.db_session.execute(query)
        symptom_log_entry = result.scalar_one_or_none()
        return symptom_log_entry

    async def create_symptom_log(self, symptom_id: int, intensity: int, timestamp: datetime, duration: int | None) -> symptom_log:
        """Create a new symptom log entry."""
        new_log = symptom_log(
            symptom_id=symptom_id,
            intensity=intensity,
            timestamp=timestamp,
            duration=duration
        )
        self.db_session.add(new_log)
        await self.db_session.commit()
        await self.db_session.refresh(new_log)
        return new_log
    
    async def delete_symptom_log(self, log_id: int) -> bool:
        """Delete a symptom log by its ID."""
        query = sa.delete(symptom_log).where(symptom_log.log_id == log_id)
        result = await self.db_session.execute(query)
        await self.db_session.commit()
        return result.rowcount > 0


    