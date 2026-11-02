"""Meal follow up routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_user
from schemas.meal_follow_up import MealFollowUpResponse
from schemas.user import UserResponse
from services.food_log_service import FoodLogService
from services.meal_follow_up_service import MealFollowUpsService

router = APIRouter(
    prefix="/meal-follow-ups",
    tags=["Meal Follow Ups"],
)


@router.get("/{food_log_id}", response_model=MealFollowUpResponse)
async def get_meal_follow_up(
    food_log_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MealFollowUpResponse:
    """
    Get the follow up notification for one of the authenticated user's food logs.
    """
    food_log_service = FoodLogService()
    food_log = food_log_service.get_food_log_by_id(db, food_log_id)
    if not food_log or food_log.username != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Food log with ID {food_log_id} not found",
        )

    meal_follow_up_service = MealFollowUpsService()
    return MealFollowUpResponse(
        should_schedule=meal_follow_up_service.should_schedule(db, food_log_id),
        fire_at=meal_follow_up_service.when_to_fire(db, food_log_id),
        title="How are you feeling?",
        body=meal_follow_up_service.build_message(db, food_log_id),
        data=MealFollowUpResponse.Data(log_type="symptom", food_log_id=food_log_id),
    )
