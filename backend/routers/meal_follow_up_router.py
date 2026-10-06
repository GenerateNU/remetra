from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_user
from schemas.meal_follow_up import MealFollowUpResponse
from schemas.user import UserResponse
from schemas.food_log import FoodLogResponse
from services.meal_follow_up_service import MealFollowUpsService
from services.food_log_service import FoodLogService
from services.food_service import FoodService

router = APIRouter(
    prefix="/meal-follow-ups",
    tags=["Meal Follow Ups"],
)

@router.get("/meal-follow-ups/{food_log_id}", response_model=MealFollowUpResponse)
async def get_meal_follow_ups(
    current_user: UserResponse = Depends(get_current_user),

) -> MealFollowUpResponse:
    """
    Get all meal follow ups for authenticated user.
    """
    
    if MealFollowUpsService.should_schedule():
        food_name = FoodService.get_food_by_id()
    


    

