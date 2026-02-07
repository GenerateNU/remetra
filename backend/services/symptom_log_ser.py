from datetime import datetime, timezone
from decimal import Decimal
import sqlalchemy as sa

class SymptomLog:  
    """SQLAlchemy model for symptom logs."""
    __tablename__ = 'symptom_logs'

    async def get_symptom_log(self, log_id: int) -> 'SymptomLog':
        """Fetch a symptom log by its ID."""
        async with self.session() as session:
            result = await session.execute(
                sa.select(SymptomLog).where(SymptomLog.log_id == log_id)
            )
            return result.scalar_one_or_none()
    
    async def create_symptom_log(self, symptom_id: int, intensity: int, timestamp: datetime, duration: int = None) -> 'SymptomLog':
        """Create a new symptom log entry."""
        async with self.session() as session:
            new_log = SymptomLog(
                symptom_id=symptom_id,
                intensity=intensity,
                timestamp=timestamp,
                duration=duration
            )
            session.add(new_log)
            await session.commit()
            await session.refresh(new_log)
            return new_log