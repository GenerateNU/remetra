import calendar
import re
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from local_day import parse_timezone
from repositories.calendar_repository import CalendarRepository
from schemas.calendar import CalendarDayResponse, CalendarDaySummary, CalendarMonthResponse
from schemas.food_log import FoodLogResponse
from schemas.symptom_log import SymptomLogResponse

MONTH_FORMAT = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])$")


class CalendarService:
    def __init__(self):
        self.repo = CalendarRepository()

    def get_month(
        self, db: Session, username: str, month: str, tz: str, today: date | None = None
    ) -> CalendarMonthResponse:
        """One summary per day of `month` (YYYY-MM), plus streaks over the user's whole history.

        `today` is the user's local date; it defaults to now in `tz`, not the server's clock.
        Raises ValueError for a malformed month or an unknown timezone.
        """
        zone = parse_timezone(tz)
        first, last = parse_month(month)
        today = today or datetime.now(zone).date()

        rows = self.repo.get_log_counts_by_local_day(db, username, tz)
        counts = {day: (food, symptoms) for day, food, symptoms in rows}
        health_dates = self.repo.get_health_dates(db, username, first, last)

        days = []
        for offset in range((last - first).days + 1):
            day = first + timedelta(days=offset)
            food, symptoms = counts.get(day, (0, 0))
            days.append(
                CalendarDaySummary(
                    date=day,
                    food_count=food,
                    symptom_count=symptoms,
                    has_health_data=day in health_dates,
                    status=day_status(food, symptoms),
                )
            )

        current_streak, longest_streak = compute_streaks(set(counts), today)
        return CalendarMonthResponse(
            month=month,
            days=days,
            current_streak=current_streak,
            longest_streak=longest_streak,
        )

    def get_day_logs(self, db: Session, username: str, day: date, tz: str) -> CalendarDayResponse:
        """A single local day's food and symptom logs, oldest first. Raises ValueError for an unknown timezone."""
        parse_timezone(tz)
        food_logs = self.repo.get_food_logs_for_day(db, username, day, tz)
        symptom_logs = self.repo.get_symptom_logs_for_day(db, username, day, tz)
        return CalendarDayResponse(
            date=day,
            food_logs=[FoodLogResponse.model_validate(log) for log in food_logs],
            symptom_logs=[SymptomLogResponse.model_validate(log) for log in symptom_logs],
        )


def parse_month(month: str) -> tuple[date, date]:
    """First and last day of a YYYY-MM month. Raises ValueError for anything else."""
    match = MONTH_FORMAT.match(month)
    if not match or int(match.group(1)) < 1:
        raise ValueError(f"month must be YYYY-MM, got {month!r}")
    year, month_number = int(match.group(1)), int(match.group(2))
    return date(year, month_number, 1), date(year, month_number, calendar.monthrange(year, month_number)[1])


def day_status(food_count: int, symptom_count: int) -> str:
    if food_count > 0 and symptom_count > 0:
        return "complete"
    if food_count > 0:
        return "food_only"
    if symptom_count > 0:
        return "symptoms_only"
    return "empty"


def compute_streaks(logged_dates: set[date], today: date) -> tuple[int, int]:
    """(current streak, longest streak) in days.

    The current streak counts back from today, or from yesterday when today isn't logged yet,
    so an unlogged morning doesn't reset it. The longest streak is over all of history.
    """
    if not logged_dates:
        return 0, 0

    sorted_dates = sorted(logged_dates)
    longest = current = 1
    for previous, day in zip(sorted_dates, sorted_dates[1:]):
        current = current + 1 if day - previous == timedelta(days=1) else 1
        longest = max(longest, current)

    check = today if today in logged_dates else today - timedelta(days=1)
    current_streak = 0
    while check in logged_dates:
        current_streak += 1
        check -= timedelta(days=1)

    return current_streak, longest
