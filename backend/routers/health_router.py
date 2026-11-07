"""
Router for health sync endpoints.

Handles HTTP requests for syncing daily health metrics and events.
"""

import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_user
from schemas.health import HealthSyncRequest, HealthSyncResponse, HealthTrendDay
from schemas.user import UserResponse
from services.health_sync_service import HealthSyncService
from services.health_trends_service import HealthTrendsService

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)

MAX_TREND_DAYS = 90

@router.post(
    "/sync",
    response_model=HealthSyncResponse,
    status_code=status.HTTP_200_OK,
)
async def sync_health_data(
    request: HealthSyncRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> HealthSyncResponse:
    """Sync health days and events for the authenticated user."""
    service = HealthSyncService()
    try:
        return service.sync(db, current_user.username, request)
    except SQLAlchemyError as e:
        logging.error(f"Error syncing health data for user {current_user.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync health data",
        ) from e

@router.get(
    "/trends",
    response_model=list[HealthTrendDay],
    status_code=status.HTTP_200_OK,
)
async def get_health_trends(
    start: date,
    end: date,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> list[HealthTrendDay]:
    """Return one entry per day from start to end with health metrics and symptom counts."""
    if end < start:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="end must be on or after start",
        )
    if (end - start).days + 1 > MAX_TREND_DAYS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Date range cannot be longer than {MAX_TREND_DAYS} days",
        )

    service = HealthTrendsService()
    try:
        return service.get_trends(db, current_user.username, start, end)
    except SQLAlchemyError as e:
        logging.error(f"Error loading health trends for user {current_user.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load health trends",
        ) from e