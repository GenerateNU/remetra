"""Router for the weekly results screen: the current user's food labels."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_user
from schemas.user import UserResponse
from schemas.weekly_results import WeeklyResultsResponse
from services.weekly_results_service import WeeklyResultsService

router = APIRouter(prefix="/results", tags=["Results"])


@router.get("/weekly", response_model=WeeklyResultsResponse, status_code=status.HTTP_200_OK)
async def get_weekly_results(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> WeeklyResultsResponse:
    """Return the signed-in user's labels: likely trigger, still learning, looks fine, and no clear pattern."""
    service = WeeklyResultsService()
    try:
        return service.get_weekly_results(db, current_user.username)
    except SQLAlchemyError as e:
        logging.error(f"Error fetching weekly results for user {current_user.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch weekly results",
        ) from e
