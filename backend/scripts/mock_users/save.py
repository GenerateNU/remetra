"""Writes generated users straight to the database with bulk inserts, replacing any existing mock_ users."""

import uuid

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from auth_context import system_access
from models.daily_health_metrics import DailyHealthMetrics
from models.food import Food
from models.food_log import FoodLog
from models.symptom import Symptom
from models.symptom_log import SymptomLog
from models.user import User
from scripts.mock_users.health import TIMEZONE
from scripts.mock_users.shapes import USERNAME_PREFIX, MockUserData

CHUNK_SIZE = 1000


def symptom_name(sensation: str, location: str) -> str:
    """Same display name AddSymptomModal gives a symptom."""
    return f"{sensation} \u2014 {location}"


def delete_mock_users(db: Session) -> int:
    """Delete mock_ users without committing. Their foods, logs and health rows cascade."""
    return db.execute(delete(User).where(User.username.startswith(USERNAME_PREFIX, autoescape=True))).rowcount


def clear_mock_users(db: Session) -> int:
    with system_access():
        removed = delete_mock_users(db)
        db.commit()
    return removed


def _rows_by_model(users: list[MockUserData]) -> list[tuple[type, list[dict]]]:
    """Insert rows per table, in foreign key order."""
    users_rows, foods, food_logs, symptoms, symptom_logs, health = [], [], [], [], [], []
    for user in users:
        users_rows.append({"username": user.username, "email": f"{user.username}@mock.remetra.test"})

        food_ids = {food.name: uuid.uuid4() for food in user.foods}
        foods += [
            {"id": food_ids[f.name], "name": f.name, "ingredients": f.ingredients, "username": user.username}
            for f in user.foods
        ]
        food_logs += [
            {"id": uuid.uuid4(), "username": user.username, "food_id": food_ids[m.food_name], "timestamp": m.timestamp}
            for m in user.meals
        ]

        symptom_ids = {}
        for event in user.symptoms:
            kind = event.symptom
            if kind not in symptom_ids:
                symptom_ids[kind] = uuid.uuid4()
                symptoms.append(
                    {
                        "id": symptom_ids[kind],
                        "username": user.username,
                        "name": symptom_name(kind.sensation, kind.location),
                        "location": kind.location,
                        "sensation": kind.sensation,
                    }
                )
            symptom_logs.append(
                {
                    "id": uuid.uuid4(),
                    "username": user.username,
                    "symptom_id": symptom_ids[kind],
                    "intensity": event.intensity,
                    "duration": event.duration_minutes,
                    "timestamp": event.timestamp,
                }
            )

        health += [{"username": user.username, "timezone": TIMEZONE, **day.model_dump()} for day in user.health_days]

    return [
        (User, users_rows),
        (Food, foods),
        (FoodLog, food_logs),
        (Symptom, symptoms),
        (SymptomLog, symptom_logs),
        (DailyHealthMetrics, health),
    ]


def save_users(db: Session, users: list[MockUserData]) -> None:
    """Replace every mock_ user with `users` in one transaction. On failure, the previous mock users stay."""
    tables = _rows_by_model(users)
    with system_access():
        with db.begin_nested():
            delete_mock_users(db)
            for model, rows in tables:
                for start in range(0, len(rows), CHUNK_SIZE):
                    db.execute(pg_insert(model).values(rows[start : start + CHUNK_SIZE]))
        db.commit()
