from collections import defaultdict
from datetime import UTC, date, timedelta, tzinfo
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from models.daily_health_metrics import DailyHealthMetrics
from repositories.health_repository import HealthRepository
from schemas.health import HealthTrendDay


class HealthTrendsService:
    """Builds a day-by-day view of a user's health metrics alongside their symptom logs."""

    def __init__(self, repository: HealthRepository | None = None):
        self.repository = repository or HealthRepository()

    def get_trends(self, db: Session, username: str, start: date, end: date) -> list[HealthTrendDay]:
        """
        Return one entry per day from start to end (will be inclusive). Days with no health data will have null metrics.
        Days with no symptoms have symptom_count 0 and max_intensity null.
        """
        health_rows = self.repository.get_days_in_range(db, username, start, end)
        symptom_logs = self.repository.get_symptom_logs_in_range(db, username, start, end)

        health_by_date = {row.date: row for row in health_rows}

        # collects all symptom logs using one timezone
        tz = self._pick_timezone(health_rows)
        intensities_by_date: dict[date, list[int]] = defaultdict(list)
        for log in symptom_logs:
            local_date = log.timestamp.astimezone(tz).date()
            if start <= local_date <= end:
                intensities_by_date[local_date].append(log.intensity)

        trends = []
        current = start
        while current <= end:
            row = health_by_date.get(current)
            intensities = intensities_by_date.get(current, [])
            trends.append(
                HealthTrendDay(
                    date=current,
                    sleep_total_min=row.sleep_total_min if row else None,
                    hrv_avg_ms=row.hrv_avg_ms if row else None,
                    resting_hr_bpm=row.resting_hr_bpm if row else None,
                    symptom_count=len(intensities),
                    max_intensity=max(intensities) if intensities else None,
                )
            )
            current += timedelta(days=1)

        return trends

    def _pick_timezone(self, health_rows: list[DailyHealthMetrics]) -> tzinfo:
        """Use the most recent synced timezone in range, falling back to UTC."""
        for row in reversed(health_rows):
            if row.timezone:
                return ZoneInfo(row.timezone)
        return UTC

    