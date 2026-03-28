"""
Fetch food and symptom log DTOs from the database for use by the analysis algorithm.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from analysis.models import FoodLogEntry, SymptomLogEntry
from models.food import Food
from models.food_log import FoodLog
from models.symptom import Symptom
from models.symptom_log import SymptomLog


def fetch_food_logs(db: Session, username: str) -> list[FoodLogEntry]:
    stmt = (
        select(FoodLog, Food)
        .join(Food, FoodLog.food_id == Food.id)
        .where(FoodLog.username == username)
        .order_by(FoodLog.timestamp.asc())
    )

    rows = db.execute(stmt).all()

    return [
        FoodLogEntry(
            timestamp=food_log.timestamp,
            # When a food has no ingredients (e.g. "orange"), treat the food
            # name itself as the ingredient so it still surfaces in analysis.
            ingredients=food.ingredients if food.ingredients else [food.name],
        )
        for food_log, food in rows
    ]


def fetch_symptom_logs(db: Session, username: str) -> list[SymptomLogEntry]:
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

    rows = db.execute(stmt).all()

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
