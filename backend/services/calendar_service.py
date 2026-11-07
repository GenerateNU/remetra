import calendar
from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from local_day import parse_timezone
from repositories.calendar_repository import CalendarRepository
from schemas.calendar import CalendarDayResponse, CalendarMonthResponse, DayLogsResponse, DayStatus
from schemas.food_log import FoodLogResponse
from schemas.symptom_log import SymptomLogResponse


def day_status(food_count: int, symptom_count: int) -> DayStatus:
    if food_count > 0 and symptom_count > 0:
        return "complete"
    if food_count > 0:
        return "food_only"
    if symptom_count > 0:
        return "symptoms_only"
    return "empty"


def compute_streaks(logged_days: set[date], today: date) -> tuple[int, int]:
    if not logged_days:
        return 0, 0

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

    def __init__(self):
        self.repo = CalendarRepository()

    def get_month(
        self, db: Session, username: str, month: str, timezone: str, today: Optional[date] = None,
    ) -> CalendarMonthResponse:
        tz = parse_timezone(timezone)
        today = today or datetime.now(tz).date()
        year, month_number = (int(part) for part in month.split("-"))
        first = date(year, month_number, 1)
        last = date(year, month_number, calendar.monthrange(year, month_number)[1])

        food_counts = self.repo.get_food_counts(db, username, first, last, timezone)
        symptom_counts = self.repo.get_symptom_counts(db, username, first, last, timezone)
        health_dates = self.repo.get_health_dates(db, username, first, last)
        all_logged = self.repo.get_all_logged_dates(db, username, timezone)

        days = []
        for offset in range((last - first).days + 1):
            d = first + timedelta(days=offset)
            fc = food_counts.get(d, 0)
            sc = symptom_counts.get(d, 0)
            days.append(CalendarDayResponse(
                date=d,
                food_count=fc,
                symptom_count=sc,
                has_health_data=d in health_dates,
                status=day_status(fc, sc),
            ))

        current, longest = compute_streaks(all_logged, today)
        return CalendarMonthResponse(
            month=month, days=days, current_streak=current, longest_streak=longest,
        )

    def get_day_logs(self, db: Session, username: str, day: date, timezone: str) -> DayLogsResponse:
        parse_timezone(timezone)
        food_logs = self.repo.get_food_logs_for_day(db, username, day, timezone)
        symptom_logs = self.repo.get_symptom_logs_for_day(db, username, day, timezone)
        return DayLogsResponse(
            date=day,
            food_logs=[FoodLogResponse.model_validate(log) for log in food_logs],
            symptom_logs=[SymptomLogResponse.model_validate(log) for log in symptom_logs],
        )
