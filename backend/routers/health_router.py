"""
Router for health sync endpoints.

Handles HTTP requests for syncing daily health metrics and events.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_user
from schemas.health import HealthSyncRequest, HealthSyncResponse
from schemas.user import UserResponse
from services.health_sync_service import HealthSyncService

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


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
