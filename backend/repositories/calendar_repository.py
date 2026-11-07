import logging
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from local_day import local_date_column
from models.daily_health_metrics import DailyHealthMetrics
from models.food_log import FoodLog
from models.symptom_log import SymptomLog

logger = logging.getLogger(__name__)


class CalendarRepository:

    def get_food_counts(
        self, db: Session, username: str, month_start: date, month_end: date, tz: str,
    ) -> dict[date, int]:
        local = local_date_column(FoodLog.timestamp, tz)
        stmt = (
            select(local.label("local_date"), func.count().label("cnt"))
            .where(
                FoodLog.username == username,
                local >= month_start,
                local <= month_end,
            )
            .group_by("local_date")
        )
        try:
            rows = db.execute(stmt).all()
            return {row.local_date: row.cnt for row in rows}
        except Exception as e:
            logger.error(f"Error fetching food counts: {e}")
            return {}

    def get_symptom_counts(
        self, db: Session, username: str, month_start: date, month_end: date, tz: str,
    ) -> dict[date, int]:
        local = local_date_column(SymptomLog.timestamp, tz)
        stmt = (
            select(local.label("local_date"), func.count().label("cnt"))
            .where(
                SymptomLog.username == username,
                local >= month_start,
                local <= month_end,
            )
            .group_by("local_date")
        )
        try:
            rows = db.execute(stmt).all()
            return {row.local_date: row.cnt for row in rows}
        except Exception as e:
            logger.error(f"Error fetching symptom counts: {e}")
            return {}

    def get_health_dates(
        self, db: Session, username: str, start: date, end: date,
    ) -> set[date]:
        stmt = select(DailyHealthMetrics.date).where(
            DailyHealthMetrics.username == username,
            DailyHealthMetrics.date >= start,
            DailyHealthMetrics.date <= end,
        )
        try:
            return set(db.execute(stmt).scalars().all())
        except Exception as e:
            logger.error(f"Error fetching health dates: {e}")
            return set()

    def get_all_logged_dates(self, db: Session, username: str, tz: str) -> set[date]:
        food_local = local_date_column(FoodLog.timestamp, tz)
        symptom_local = local_date_column(SymptomLog.timestamp, tz)
        food_dates = select(food_local.label("local_date")).where(FoodLog.username == username)
        symptom_dates = select(symptom_local.label("local_date")).where(SymptomLog.username == username)
        union = food_dates.union(symptom_dates)
        try:
            return set(db.execute(union).scalars().all())
        except Exception as e:
            logger.error(f"Error fetching all logged dates: {e}")
            return set()

    def get_food_logs_for_day(
        self, db: Session, username: str, day: date, tz: str,
    ) -> list[FoodLog]:
        local = local_date_column(FoodLog.timestamp, tz)
        stmt = (
            select(FoodLog)
            .where(FoodLog.username == username, local == day)
            .order_by(FoodLog.timestamp)
        )
        try:
            return list(db.execute(stmt).scalars().all())
        except Exception as e:
            logger.error(f"Error fetching food logs for day: {e}")
            return []

    def get_symptom_logs_for_day(
        self, db: Session, username: str, day: date, tz: str,
    ) -> list[SymptomLog]:
        local = local_date_column(SymptomLog.timestamp, tz)
        stmt = (
            select(SymptomLog)
            .where(SymptomLog.username == username, local == day)
            .order_by(SymptomLog.timestamp)
        )
        try:
            return list(db.execute(stmt).scalars().all())
        except Exception as e:
            logger.error(f"Error fetching symptom logs for day: {e}")
            return []
