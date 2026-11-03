"""
Router for daily check-in endpoints.

Handles HTTP requests for recording "no symptoms" check-ins.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_user
from schemas.daily_check_in import DailyCheckInCreate, DailyCheckInResponse
from schemas.user import UserResponse
from services.daily_check_in_service import DailyCheckInService

router = APIRouter(
    prefix="/check-ins",
    tags=["Check-ins"],
)


@router.post(
    "/no-symptoms",
    response_model=DailyCheckInResponse,
    status_code=status.HTTP_200_OK,
)
async def check_in_no_symptoms(
    check_in: DailyCheckInCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> DailyCheckInResponse:
    """Mark a local date as symptom-free. Repeating for the same date returns the same check-in."""
    service = DailyCheckInService()
    return service.check_in_no_symptoms(db, current_user.username, check_in)
