from datetime import date, datetime, time, timedelta

from sqlalchemy import func, literal, select, union_all
from sqlalchemy.orm import Session, joinedload

from local_day import local_date_column, parse_timezone
from models.daily_health_metrics import DailyHealthMetrics
from models.food_log import FoodLog
from models.symptom_log import SymptomLog


class CalendarRepository:
    def get_log_counts_by_local_day(self, db: Session, username: str, tz: str) -> list[tuple[date, int, int]]:
        """(local day, food count, symptom count) for every day the user logged anything, oldest first.

        One query over the user's whole history: the month grid and the streaks both come from it,
        so the number of queries stays the same however long the history gets.
        """
        food = select(
            local_date_column(FoodLog.timestamp, tz).label("day"),
            literal(1).label("food"),
            literal(0).label("symptom"),
        ).where(FoodLog.username == username)
        symptoms = select(
            local_date_column(SymptomLog.timestamp, tz).label("day"),
            literal(0).label("food"),
            literal(1).label("symptom"),
        ).where(SymptomLog.username == username)
        logs = union_all(food, symptoms).subquery()

        stmt = (
            select(logs.c.day, func.sum(logs.c.food), func.sum(logs.c.symptom))
            .group_by(logs.c.day)
            .order_by(logs.c.day)
        )
        return [(day, int(food_count), int(symptom_count)) for day, food_count, symptom_count in db.execute(stmt)]

    def get_health_dates(self, db: Session, username: str, start: date, end: date) -> set[date]:
        """Days between start and end (inclusive) that have synced health data."""
        stmt = select(DailyHealthMetrics.date).where(
            DailyHealthMetrics.username == username,
            DailyHealthMetrics.date >= start,
            DailyHealthMetrics.date <= end,
        )
        return set(db.execute(stmt).scalars().all())

    def get_food_logs_for_day(self, db: Session, username: str, day: date, tz: str) -> list[FoodLog]:
        start, end = _local_day_bounds(day, tz)
        stmt = (
            select(FoodLog)
            .where(FoodLog.username == username, FoodLog.timestamp >= start, FoodLog.timestamp < end)
            .order_by(FoodLog.timestamp)
        )
        return list(db.execute(stmt).scalars().all())

    def get_symptom_logs_for_day(self, db: Session, username: str, day: date, tz: str) -> list[SymptomLog]:
        start, end = _local_day_bounds(day, tz)
        stmt = (
            select(SymptomLog)
            .options(joinedload(SymptomLog.symptom))  # the response routes each log by its symptom
            .where(SymptomLog.username == username, SymptomLog.timestamp >= start, SymptomLog.timestamp < end)
            .order_by(SymptomLog.timestamp)
        )
        return list(db.execute(stmt).unique().scalars().all())


def _local_day_bounds(day: date, tz: str) -> tuple[datetime, datetime]:
    """Start (inclusive) and end (exclusive) instants of a local calendar day; DST days are 23 or 25 hours."""
    zone = parse_timezone(tz)
    return (
        datetime.combine(day, time.min, tzinfo=zone),
        datetime.combine(day + timedelta(days=1), time.min, tzinfo=zone),
    )
