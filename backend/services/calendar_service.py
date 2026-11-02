"""Service layer for the logging calendar."""

import calendar
import logging
from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from local_day import parse_timezone
from repositories.calendar_repository import CalendarRepository
from schemas.calendar import CalendarDayResponse, CalendarMonthResponse, DayLogsResponse, DayStatus
from schemas.food_log import FoodLogResponse
from schemas.symptom_log import SymptomLogResponse


def day_status(food_count: int, symptom_count: int) -> DayStatus:
    """The one place a day's status is decided; the app only displays it."""
    if food_count > 0 and symptom_count > 0:
        return "complete"
    if food_count > 0:
        return "food_only"
    if symptom_count > 0:
        return "symptoms_only"
    return "empty"


def compute_streaks(logged_days: set[date], today: date) -> tuple[int, int]:
    """
    (current, longest) runs of consecutive days with at least one log.

    Any log counts, not only complete days: a symptom-free day is "food only" for now, and it
    shouldn't break a streak. The current streak counts back from today, or from yesterday if
    today has nothing yet, so it doesn't reset before the user has had a chance to log.
    """
    current = 0
    cursor = today if today in logged_days else today - timedelta(days=1)
    while cursor in logged_days:
        current += 1
        cursor -= timedelta(days=1)

    longest = 0
    run = 0
    previous: Optional[date] = None
    for day in sorted(logged_days):
        run = run + 1 if previous is not None and day - previous == timedelta(days=1) else 1
        longest = max(longest, run)
        previous = day

    return current, longest


class CalendarService:
    """Builds the month summary and the day's logs, grouped by the user's local day."""

    def __init__(self):
        self.repo = CalendarRepository()

    def get_month(
        self, db: Session, username: str, month: str, timezone: str, today: Optional[date] = None
    ) -> CalendarMonthResponse:
        """One entry per day of `month` (YYYY-MM), plus streaks over the user's whole history."""
        tz = parse_timezone(timezone)
        today = today or datetime.now(tz).date()
        year, month_number = (int(part) for part in month.split("-"))
        first = date(year, month_number, 1)
        last = date(year, month_number, calendar.monthrange(year, month_number)[1])
        logging.info("Building calendar for %s, %s in %s", username, month, timezone)

        counts = {
            day: (food, symptom) for day, food, symptom in self.repo.get_log_counts_by_local_day(db, username, timezone)
        }
        health_dates = self.repo.get_health_dates(db, username, first, last)

        days = []
        for offset in range((last - first).days + 1):
            day = first + timedelta(days=offset)
            food, symptom = counts.get(day, (0, 0))
            days.append(
                CalendarDayResponse(
                    date=day,
                    food_count=food,
                    symptom_count=symptom,
                    has_health_data=day in health_dates,
                    status=day_status(food, symptom),
                )
            )

        current, longest = compute_streaks(set(counts), today)
        return CalendarMonthResponse(month=month, days=days, current_streak=current, longest_streak=longest)

    def get_day_logs(self, db: Session, username: str, day: date, timezone: str) -> DayLogsResponse:
        """Every food and symptom log on one local day, oldest first."""
        parse_timezone(timezone)
        food_logs = self.repo.get_food_logs_on_local_day(db, username, timezone, day)
        symptom_logs = self.repo.get_symptom_logs_on_local_day(db, username, timezone, day)
        return DayLogsResponse(
            date=day,
            food_logs=[FoodLogResponse.model_validate(log) for log in food_logs],
            symptom_logs=[SymptomLogResponse.model_validate(log) for log in symptom_logs],
        )
