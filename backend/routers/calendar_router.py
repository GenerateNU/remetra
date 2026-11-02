"""Logging calendar routes."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_user
from schemas.calendar import CalendarMonthResponse, DayLogsResponse, MonthKey, TimezoneName
from schemas.user import UserResponse
from services.calendar_service import CalendarService

router = APIRouter(
    prefix="/calendar",
    tags=["Calendar"],
    dependencies=[Depends(get_current_user)],
)

Timezone = Annotated[TimezoneName, Query(alias="tz", description="IANA timezone of the device, e.g. America/New_York")]


@router.get("/month", response_model=CalendarMonthResponse)
async def get_calendar_month(
    month: Annotated[MonthKey, Query(description="YYYY-MM")],
    timezone: Timezone,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> CalendarMonthResponse:
    """
    How completely each day of a month was logged, grouped by the user's local day, with streaks.
    """
    service = CalendarService()
    return service.get_month(db, current_user.username, month, timezone)


@router.get("/day", response_model=DayLogsResponse)
async def get_calendar_day(
    day: Annotated[date, Query(alias="date", description="YYYY-MM-DD")],
    timezone: Timezone,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> DayLogsResponse:
    """
    Every food and symptom log on one local day, oldest first.
    """
    service = CalendarService()
    return service.get_day_logs(db, current_user.username, day, timezone)
