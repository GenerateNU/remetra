import logging
from datetime import date

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from models.daily_health_metrics import DailyHealthMetrics
from models.food_log import FoodLog
from models.symptom_log import SymptomLog


class CalendarRepository:

    def get_food_counts(
        self, db: Session, username: str, month_start: date, month_end: date, tz: str,
    ) -> dict[date, int]:
        stmt = (
            select(
                func.date(FoodLog.timestamp.op("AT TIME ZONE")(text(f"'{tz}'"))).label("local_date"),
                func.count().label("cnt"),
            )
            .where(
                FoodLog.username == username,
                FoodLog.timestamp >= text(f"'{month_start}'::date AT TIME ZONE '{tz}'"),
                FoodLog.timestamp < text(f"('{month_end}'::date + 1) AT TIME ZONE '{tz}'"),
            )
            .group_by("local_date")
        )
        try:
            rows = db.execute(stmt).all()
            return {row.local_date: row.cnt for row in rows}
        except Exception as e:
            logging.error(f"Error fetching food counts: {e}")
            return {}

    def get_symptom_counts(
        self, db: Session, username: str, month_start: date, month_end: date, tz: str,
    ) -> dict[date, int]:
        stmt = (
            select(
                func.date(SymptomLog.timestamp.op("AT TIME ZONE")(text(f"'{tz}'"))).label("local_date"),
                func.count().label("cnt"),
            )
            .where(
                SymptomLog.username == username,
                SymptomLog.timestamp >= text(f"'{month_start}'::date AT TIME ZONE '{tz}'"),
                SymptomLog.timestamp < text(f"('{month_end}'::date + 1) AT TIME ZONE '{tz}'"),
            )
            .group_by("local_date")
        )
        try:
            rows = db.execute(stmt).all()
            return {row.local_date: row.cnt for row in rows}
        except Exception as e:
            logging.error(f"Error fetching symptom counts: {e}")
            return {}

    def get_health_synced_dates(self, db: Session, username: str, month_start: date, month_end: date) -> set[date]:
        stmt = (
            select(DailyHealthMetrics.date)
            .where(
                DailyHealthMetrics.username == username,
                DailyHealthMetrics.date >= month_start,
                DailyHealthMetrics.date <= month_end,
            )
        )
        try:
            rows = db.execute(stmt).scalars().all()
            return set(rows)
        except Exception as e:
            logging.error(f"Error fetching health synced dates: {e}")
            return set()

    def get_food_logs_for_day(
        self, db: Session, username: str, day: date, tz: str,
    ) -> list[FoodLog]:
        stmt = (
            select(FoodLog)
            .where(
                FoodLog.username == username,
                FoodLog.timestamp >= text(f"'{day}'::date AT TIME ZONE '{tz}'"),
                FoodLog.timestamp < text(f"('{day}'::date + 1) AT TIME ZONE '{tz}'"),
            )
            .order_by(FoodLog.timestamp)
        )
        try:
            return list(db.execute(stmt).scalars().all())
        except Exception as e:
            logging.error(f"Error fetching food logs for day: {e}")
            return []

    def get_symptom_logs_for_day(
        self, db: Session, username: str, day: date, tz: str,
    ) -> list[SymptomLog]:
        stmt = (
            select(SymptomLog)
            .where(
                SymptomLog.username == username,
                SymptomLog.timestamp >= text(f"'{day}'::date AT TIME ZONE '{tz}'"),
                SymptomLog.timestamp < text(f"('{day}'::date + 1) AT TIME ZONE '{tz}'"),
            )
            .order_by(SymptomLog.timestamp)
        )
        try:
            return list(db.execute(stmt).scalars().all())
        except Exception as e:
            logging.error(f"Error fetching symptom logs for day: {e}")
            return []

    def get_all_logged_dates(self, db: Session, username: str, tz: str) -> set[date]:
        food_dates = (
            select(
                func.date(FoodLog.timestamp.op("AT TIME ZONE")(text(f"'{tz}'"))).label("local_date"),
            )
            .where(FoodLog.username == username)
        )
        symptom_dates = (
            select(
                func.date(SymptomLog.timestamp.op("AT TIME ZONE")(text(f"'{tz}'"))).label("local_date"),
            )
            .where(SymptomLog.username == username)
        )
        union = food_dates.union(symptom_dates)
        try:
            rows = db.execute(union).scalars().all()
            return set(rows)
        except Exception as e:
            logging.error(f"Error fetching all logged dates: {e}")
            return set()
