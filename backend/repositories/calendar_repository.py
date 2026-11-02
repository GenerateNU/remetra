import logging
from datetime import date

from sqlalchemy import literal, select, union_all
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from local_day import local_date_column
from models.daily_health_metrics import DailyHealthMetrics
from models.food_log import FoodLog
from models.symptom_log import SymptomLog

logger = logging.getLogger(__name__)


class CalendarRepository:
    """Read-only queries behind the logging calendar. Grouping by local day happens in Postgres."""

    def get_log_counts_by_local_day(self, db: Session, username: str, timezone: str) -> list[tuple[date, int, int]]:
        """
        Food and symptom log counts for every local day the user logged anything, oldest first.

        One query over both tables and the whole history, so the cost doesn't grow with the
        number of queries as history grows. It returns at most one row per logged day, which is
        what streaks need anyway; the caller slices out the month it wants.
        """
        logger.info("Counting logs by local day for user %s in %s", username, timezone)
        food = select(
            local_date_column(FoodLog.timestamp, timezone).label("day"),
            literal(1).label("food"),
            literal(0).label("symptom"),
        ).where(FoodLog.username == username)
        symptom = select(
            local_date_column(SymptomLog.timestamp, timezone).label("day"),
            literal(0).label("food"),
            literal(1).label("symptom"),
        ).where(SymptomLog.username == username)
        logs = union_all(food, symptom).subquery()

        stmt = (
            select(logs.c.day, func.sum(logs.c.food), func.sum(logs.c.symptom))
            .group_by(logs.c.day)
            .order_by(logs.c.day)
        )
        return [(day, int(food_count), int(symptom_count)) for day, food_count, symptom_count in db.execute(stmt)]

    def get_health_dates(self, db: Session, username: str, start: date, end: date) -> set[date]:
        """
        Days from start to end (inclusive) with synced health data.

        Health rows aren't covered by the ownership filter yet, so this filters by user itself.
        Their dates are already local days, bucketed on the phone at sync time.
        """
        stmt = select(DailyHealthMetrics.date).where(
            DailyHealthMetrics.username == username,
            DailyHealthMetrics.date >= start,
            DailyHealthMetrics.date <= end,
        )
        return set(db.execute(stmt).scalars())

    def get_food_logs_on_local_day(self, db: Session, username: str, timezone: str, day: date) -> list[FoodLog]:
        """Food logs whose timestamp falls on `day` in `timezone`, oldest first."""
        return (
            db.query(FoodLog)
            .filter(FoodLog.username == username, local_date_column(FoodLog.timestamp, timezone) == day)
            .order_by(FoodLog.timestamp)
            .all()
        )

    def get_symptom_logs_on_local_day(self, db: Session, username: str, timezone: str, day: date) -> list[SymptomLog]:
        """Symptom logs whose timestamp falls on `day` in `timezone`, oldest first."""
        return (
            db.query(SymptomLog)
            .filter(SymptomLog.username == username, local_date_column(SymptomLog.timestamp, timezone) == day)
            .order_by(SymptomLog.timestamp)
            .all()
        )
