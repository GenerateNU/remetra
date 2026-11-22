import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_user
from schemas.calendar import CalendarDayResponse, CalendarMonthResponse
from schemas.user import UserResponse
from services.calendar_service import CalendarService

router = APIRouter(
    prefix="/calendar",
    tags=["Calendar"],
)


@router.get(
    "/month",
    response_model=CalendarMonthResponse,
    status_code=status.HTTP_200_OK,
)
async def get_calendar_month(
    month: str = Query(..., description="Month in YYYY-MM format, e.g. 2026-10"),
    tz: str = Query(..., description="IANA timezone of the device, e.g. America/New_York"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> CalendarMonthResponse:
    service = CalendarService()
    try:
        return service.get_month(db, current_user.username, month, tz)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)) from e
    except SQLAlchemyError as e:
        logging.error(f"Error fetching calendar for user {current_user.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch calendar data",
        ) from e


@router.get(
    "/day",
    response_model=CalendarDayResponse,
    status_code=status.HTTP_200_OK,
)
async def get_calendar_day(
    day: date = Query(..., alias="date", description="Local day in YYYY-MM-DD format"),
    tz: str = Query(..., description="IANA timezone of the device, e.g. America/New_York"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> CalendarDayResponse:
    service = CalendarService()
    try:
        return service.get_day_logs(db, current_user.username, day, tz)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)) from e
    except SQLAlchemyError as e:
        logging.error(f"Error fetching day logs for user {current_user.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch day logs",
        ) from e
