""" 
This is where you will define the functions for getting the food/symptom
Log entry DTOsw from joining the food/symptom table with the food/symptom log table
"""
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select

from .models import FoodLogEntry, SymptomLogEntry
from backend.models.symptom import Symptom
from backend.models.symptom_log import SymptomLog


async def fetch_food_logs(db: Session, username: str) -> list[FoodLogEntry]: 
  return

async def fetch_symptom_logs(db: AsyncSession, username: str) -> list[SymptomLogEntry]: 
  stmt = (select(
        Symptom.name,
        Symptom.location,
        Symptom.sensation,
        SymptomLog.intensity,
        SymptomLog.timestamp,
        SymptomLog.duration
    ).select_from(SymptomLog)
    .join(Symptom, SymptomLog.symptom_id == Symptom.id)
    .where(SymptomLog.username == username)
    .order_by(SymptomLog.timestamp.asc()))
  
  results = await db.execute(stmt)
  rows = results.all()

  return [SymptomLogEntry(
    symptom_name=row.name,
    location=row.location,
    sensation=row.sensation,
    intensity=row.intensity,
    timestamp=row.timestamp,
    duration=row.duration)
    for row in rows]
