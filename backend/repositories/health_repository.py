import logging
from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from models.daily_health_metrics import DailyHealthMetrics
from models.healthkit_event import HealthKitEvent
from models.symptom_log import SymptomLog
from schemas.health import HealthDayEntry, HealthEventEntry

DAY_METRIC_FIELDS = (
    "sleep_total_min",
    "sleep_deep_min",
    "sleep_rem_min",
    "sleep_core_min",
    "sleep_awake_min",
    "hrv_avg_ms",
    "resting_hr_bpm",
)


class HealthRepository:
    """
    Repository for persisting HealthKit sync data (daily metrics and discrete events).
    """

    def save_days(self, db: Session, username: str, timezone: str, days: list[HealthDayEntry]) -> int:
        """
        Upsert daily health metrics. One row per (username, date); re-syncing a day overwrites it.

        Args:
            username: Owner of the metrics
            timezone: Client timezone the days were bucketed in
            days: Validated day entries from the sync request

        Returns:
            Number of days saved (inserted or updated)
        """
        if not days:
            return 0

        # Postgres rejects an upsert that touches the same row twice, so keep the last entry per date
        rows_by_date = {day.date: {"username": username, "timezone": timezone, **day.model_dump()} for day in days}
        rows = list(rows_by_date.values())

        logging.info(f"Upserting {len(rows)} health days for user {username}")

        try:
            stmt = pg_insert(DailyHealthMetrics).values(rows)
            stmt = stmt.on_conflict_do_update(
                constraint="uq_daily_health_user_date",
                set_={
                    "timezone": stmt.excluded.timezone,
                    **{field: stmt.excluded[field] for field in DAY_METRIC_FIELDS},
                    # onupdate= does not fire for ON CONFLICT, so bump it explicitly
                    "updated_at": func.now(),
                },
            )
            db.execute(stmt)
            db.commit()
            return len(rows)
        except Exception as e:
            logging.error(f"Error saving health days: {e}")
            db.rollback()
            raise e

    def save_events(self, db: Session, username: str, events: list[HealthEventEntry]) -> int:
        """
        Insert HealthKit events, skipping any whose hk_uuid was already synced for this user.

        Args:
            username: Owner of the events
            events: Validated event entries from the sync request

        Returns:
            Number of events newly inserted (skipped = len(events) - returned value)
        """
        if not events:
            return 0

        rows = [{"username": username, **event.model_dump()} for event in events]

        logging.info(f"Inserting up to {len(rows)} HealthKit events for user {username}")

        try:
            stmt = (
                pg_insert(HealthKitEvent)
                .values(rows)
                .on_conflict_do_nothing(constraint="uq_healthkit_user_hkuuid")
                .returning(HealthKitEvent.id)
            )
            inserted_ids = db.execute(stmt).scalars().all()
            db.commit()
            return len(inserted_ids)
        except Exception as e:
            logging.error(f"Error saving HealthKit events: {e}")
            db.rollback()
            raise e

    def get_days_in_range(self, db: Session, username: str, start: date, end: date) -> list[DailyHealthMetrics]:
        """
        Fetch a user's daily health metrics between the start and end date (inclusive). Days with no
        synced data have no row.
        """
        stmt = (
            select(DailyHealthMetrics)
            .where(
                DailyHealthMetrics.username == username,
                DailyHealthMetrics.date >= start,
                DailyHealthMetrics.date <= end,
            )
            .order_by(DailyHealthMetrics.date)
        )
        return list(db.execute(stmt).scalars().all())

    def get_symptom_logs_in_range(self, db: Session, username: str, start: date, end: date) -> list[SymptomLog]:
        """
        Fetch a user's symptom logs that could fall on a local date between start and end.
        Made sure window is padded by a day on each side because a log's local date can differ from its UTC date. The
        service filters each log down to its exact local date.
        """
        window_start = datetime.combine(start - timedelta(days=1), time.min, tzinfo=UTC)
        window_end = datetime.combine(end + timedelta(days=2), time.min, tzinfo=UTC)

        stmt = select(SymptomLog).where(
            SymptomLog.username == username,
            SymptomLog.timestamp >= window_start,
            SymptomLog.timestamp < window_end,
        )
        return list(db.execute(stmt).scalars().all())
