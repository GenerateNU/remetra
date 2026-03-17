"""
This is where you will define the functions for getting the food/symptom
Log entry DTOsw from joining the food/symptom table with the food/symptom log table
"""

from backend.models.food import Food
from backend.models.food_log import FoodLog
from backend.models.symptom import Symptom
from backend.models.symptom_log import SymptomLog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import FoodLogEntry, SymptomLogEntry


async def fetch_food_logs(db: AsyncSession, username: str) -> list[FoodLogEntry]:
    stmt = (
        select(FoodLog, Food)
        .join(Food, FoodLog.food_id == Food.id)
        .where(FoodLog.username == username)
        .order_by(FoodLog.timestamp.asc())
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        FoodLogEntry(
            timestamp=food_log.timestamp,
            ingredients=food.ingredients,
            # servings = food_log.quantity
        )
        for food_log, food in rows
    ]


async def fetch_symptom_logs(db: AsyncSession, username: str) -> list[SymptomLogEntry]:
    stmt = (
        select(
            Symptom.name,
            Symptom.location,
            Symptom.sensation,
            SymptomLog.intensity,
            SymptomLog.timestamp,
            SymptomLog.duration,
        )
        .select_from(SymptomLog)
        .join(Symptom, SymptomLog.symptom_id == Symptom.id)
        .where(SymptomLog.username == username)
        .order_by(SymptomLog.timestamp.asc())
    )

    results = await db.execute(stmt)
    rows = results.all()

    return [
        SymptomLogEntry(
            symptom_name=row.name,
            location=row.location,
            sensation=row.sensation,
            intensity=row.intensity,
            timestamp=row.timestamp,
            duration=row.duration,
        )
        for row in rows
    ]
