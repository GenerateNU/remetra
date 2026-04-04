"""Food log routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_user
from schemas.food_log import FoodLogCreate, FoodLogResponse, FoodLogUpdate
from schemas.user import UserResponse
from services.food_log_service import FoodLogService

router = APIRouter(prefix="/food-log", tags=["Food Logs"],)


@router.post("/", response_model=FoodLogResponse, status_code=status.HTTP_201_CREATED)
async def create_food_log(food_log: FoodLogCreate, db: Session = Depends(get_db)) -> FoodLogResponse:
    """
    Create a new food log entry.
    """
    food_log_service = FoodLogService()
    created_food_log = food_log_service.create_food_log(db, food_log)
    return created_food_log


@router.get("/user/me", response_model=list[FoodLogResponse])
async def get_my_food_logs(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> list[FoodLogResponse]:
    """
    Get all food logs for the authenticated user.
    """
    food_log_service = FoodLogService()
    return food_log_service.get_food_logs_by_username(db, current_user.username)


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


@router.put("/{food_log_id}", response_model=FoodLogResponse)
async def update_food_log(food_log_id: UUID, payload: FoodLogUpdate, db: Session = Depends(get_db)) -> FoodLogResponse:
    """Update a food log by ID."""
    food_log_service = FoodLogService()
    updated = food_log_service.update_food_log(db, food_log_id, payload)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Food log with ID {food_log_id} not found",
        )
    return updated


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
