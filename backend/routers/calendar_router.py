import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_user
from schemas.calendar import (
    CalendarDayRequest,
    CalendarDayResponse,
    CalendarMonthRequest,
    CalendarMonthResponse,
)
from schemas.user import UserResponse
from services.calendar_service import CalendarService

router = APIRouter(
    prefix="/calendar",
    tags=["Calendar"],
)


@router.post(
    "/month",
    response_model=CalendarMonthResponse,
    status_code=status.HTTP_200_OK,
)
async def get_calendar_month(
    request: CalendarMonthRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> CalendarMonthResponse:
    service = CalendarService()
    try:
        return service.get_month(db, current_user.username, request)
    except SQLAlchemyError as e:
        logging.error(f"Error fetching calendar for user {current_user.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch calendar data",
        ) from e


@router.post(
    "/day",
    response_model=CalendarDayResponse,
    status_code=status.HTTP_200_OK,
)
async def get_calendar_day(
    request: CalendarDayRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> CalendarDayResponse:
    service = CalendarService()
    try:
        return service.get_day(db, current_user.username, request)
    except SQLAlchemyError as e:
        logging.error(f"Error fetching day logs for user {current_user.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch day logs",
        ) from e
