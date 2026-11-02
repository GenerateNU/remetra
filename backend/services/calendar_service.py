import calendar
from datetime import date, timedelta

from sqlalchemy.orm import Session

from repositories.calendar_repository import CalendarRepository
from schemas.calendar import (
    CalendarDayRequest,
    CalendarDayResponse,
    CalendarDaySummary,
    CalendarMonthRequest,
    CalendarMonthResponse,
)
from schemas.food_log import FoodLogResponse
from schemas.symptom_log import SymptomLogResponse


class CalendarService:

    def __init__(self):
        self.repo = CalendarRepository()

    def get_month(self, db: Session, username: str, request: CalendarMonthRequest) -> CalendarMonthResponse:
        year, month = (int(x) for x in request.month.split("-"))
        month_start = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        month_end = date(year, month, last_day)

        food_counts = self.repo.get_food_counts(db, username, month_start, month_end, request.timezone)
        symptom_counts = self.repo.get_symptom_counts(db, username, month_start, month_end, request.timezone)
        health_dates = self.repo.get_health_synced_dates(db, username, month_start, month_end)
        all_logged = self.repo.get_all_logged_dates(db, username, request.timezone)

        days = []
        current = month_start
        while current <= month_end:
            fc = food_counts.get(current, 0)
            sc = symptom_counts.get(current, 0)
            hs = current in health_dates
            days.append(CalendarDaySummary(
                date=current,
                food_count=fc,
                symptom_count=sc,
                health_synced=hs,
                status=_day_status(fc, sc),
            ))
            current += timedelta(days=1)

        current_streak, longest_streak = _compute_streaks(all_logged)

        return CalendarMonthResponse(
            days=days,
            current_streak=current_streak,
            longest_streak=longest_streak,
        )

    def get_day(self, db: Session, username: str, request: CalendarDayRequest) -> CalendarDayResponse:
        food_logs = self.repo.get_food_logs_for_day(db, username, request.date, request.timezone)
        symptom_logs = self.repo.get_symptom_logs_for_day(db, username, request.date, request.timezone)
        return CalendarDayResponse(
            date=request.date,
            food_logs=[FoodLogResponse.model_validate(log) for log in food_logs],
            symptom_logs=[SymptomLogResponse.model_validate(log) for log in symptom_logs],
        )


def _day_status(food_count: int, symptom_count: int) -> str:
    if food_count > 0 and symptom_count > 0:
        return "complete"
    if food_count > 0:
        return "food_only"
    if symptom_count > 0:
        return "symptoms_only"
    return "empty"


def _compute_streaks(logged_dates: set[date]) -> tuple[int, int]:
    if not logged_dates:
        return 0, 0

    sorted_dates = sorted(logged_dates)
    longest = 1
    current = 1

    for i in range(1, len(sorted_dates)):
        if sorted_dates[i] - sorted_dates[i - 1] == timedelta(days=1):
            current += 1
            longest = max(longest, current)
        else:
            current = 1

    today = date.today()
    start = today if today in logged_dates else today - timedelta(days=1)
    current_streak = 0
    check = start
    while check in logged_dates:
        current_streak += 1
        check -= timedelta(days=1)

    return current_streak, longest
