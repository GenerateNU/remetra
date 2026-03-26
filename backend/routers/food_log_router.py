"""Food log routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from services.food_log_service import FoodLogService
from sqlalchemy.orm import Session

from database import get_db
from schemas.food_log import FoodLogCreate, FoodLogResponse

router = APIRouter(prefix="/food-log")


@router.post("/", response_model=FoodLogResponse, status_code=status.HTTP_201_CREATED)
async def create_food_log(food_log: FoodLogCreate, db: Session = Depends(get_db)) -> FoodLogResponse:
    """
    Create a new food log entry.
    """
    food_log_service = FoodLogService()
    created_food_log = food_log_service.create_food_log(db, food_log)
    return created_food_log

@router.get("/user/{username}", response_model=list[FoodLogResponse])
async def get_food_logs_by_username(username: str, db: Session = Depends(get_db)) -> list[FoodLogResponse]:
    """
    Get all food logs for a given user.
    """
    food_log_service = FoodLogService()
    return food_log_service.get_food_logs_by_username(db, username)

@router.get("/{food_log_id}", response_model=FoodLogResponse)
async def get_food_log(food_log_id: UUID, db: Session = Depends(get_db)) -> FoodLogResponse:
    """
    Get a specific food log by ID.
    """
    food_log_service = FoodLogService()
    food_log = food_log_service.get_food_log_by_id(db, food_log_id)
    if not food_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Food log with ID {food_log_id} not found",
        )
    return food_log


@router.delete("/{food_log_id}", response_model=FoodLogResponse)
async def delete_food_log(food_log_id: UUID, db: Session = Depends(get_db)) -> FoodLogResponse:
    """
    Delete a food log by ID.
    """
    food_log_service = FoodLogService()
    deleted_food_log = food_log_service.delete_food_log_by_id(db, food_log_id)
    if not deleted_food_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Food log with ID {food_log_id} not found",
        )
    return deleted_food_log