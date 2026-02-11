"""Authentication routes for food CRUD."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.food import FoodCreate, FoodResponse
from services.food_service import FoodService

router = APIRouter(prefix="/food")


# create food
@router.post("/", response_model=FoodResponse, status_code=status.HTTP_201_CREATED)
async def create_food(food: FoodCreate, db: Session = Depends(get_db)) -> FoodResponse:
    """
    Creates new food item with ID, name, ingredients.

    """

    food_service = FoodService()
    created_food = food_service.create_food(db, food)
    return created_food


# get food
@router.get("/{food_id}", response_model=FoodResponse)
async def get_food(food_id: int, db: Session = Depends(get_db)) -> FoodResponse:
    """
    Get a specific food by ID.

    Path parameters (like {food_id}) are extracted from the URL automatically.
    Example: GET /foods/42 → food_id = 42

    Args:
        food_id: ID from URL path parameter

    Returns:
        The requested food

    Raises:
        HTTPException: If food ID doesn't exist
    """
    food_service = FoodService()
    food = food_service.get_food_by_id(db, food_id)

    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"food with ID {food_id} not found",
        )

    return food


# get all food items
@router.get(
    "/",
    response_model=list[FoodResponse],
)
async def get_all_foods(db: Session = Depends(get_db)) -> list[FoodResponse]:
    """
    Get all food items.

    Returns:
        List of all food items
    """

    food_service = FoodService()
    foods = food_service.get_all_foods(db)
    return foods


# put route - update food
@router.put("/{food_id}", response_model=FoodResponse)
async def update_food(food_id: int, food: FoodCreate, db: Session = Depends(get_db)) -> FoodResponse:
    """
    Update an existing food by ID.

    Args:
        food_id: ID of the food to update
        food: Updated food data

    Returns:
        The updated food

    Raises:
        HTTPException: If food ID doesn't exist or input data is invalid
    """
    food_service = FoodService()
    food_dict = food.model_dump()
    updated_food = food_service.update_food_by_id(db, food_id, food_dict)

    if not updated_food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"food with ID {food_id} not found",
        )

    return updated_food


# delete route - delete food
@router.delete("/{food_id}", response_model=FoodResponse)
async def delete_food(food_id: int, db: Session = Depends(get_db)) -> FoodResponse:
    """Delete an existing food by ID.

    Args:
        food_id (int): ID of the food to update

    Returns:
        FoodResponse: The deleted food

    Raises:
        HTTPException: If food ID doesn't exist
    """
    food_service = FoodService()
    deleted_food = food_service.delete_food_by_id(db, food_id)
    if not deleted_food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"food with ID {food_id} not found",
        )

    return deleted_food
