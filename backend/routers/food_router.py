"""Authentication routes for food CRUD."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.food import FoodCreate, FoodResponse, FoodSuggestionRequest
from schemas.tag import SuggestedTagsAndIngredientsResponse
from services.food_service import FoodService
from services.RAGTaggingService import RAGTaggingService

router = APIRouter(prefix="/food")


# create food
@router.post("/", response_model=FoodResponse, status_code=status.HTTP_201_CREATED)
async def create_food(food: FoodCreate, db: Session = Depends(get_db)) -> FoodResponse:
    """Creates new food item with ID, name, ingredients."""
    food_service = FoodService()
    created_food = food_service.create_food(db, food)
    return created_food


# suggest ingredients and trigger buckets — must be above /{food_id} to avoid route clash
@router.post("/suggestions", response_model=SuggestedTagsAndIngredientsResponse)
async def suggest_tags(
    body: FoodSuggestionRequest,
    db: Session = Depends(get_db),
) -> SuggestedTagsAndIngredientsResponse:
    """
    Return LLM/RAG-suggested trigger ingredients and bucket tags for a draft food item.
    No data is persisted.
    """
    rag_service = RAGTaggingService()
    return rag_service.suggest(db, food_name=body.name, ingredients=body.ingredients)


@router.get("/{food_id}", response_model=FoodResponse)
async def get_food(food_id: int, db: Session = Depends(get_db)) -> FoodResponse:
    """Get a specific food by ID."""
    food_service = FoodService()
    food = food_service.get_food_by_id(db, food_id)
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"food with ID {food_id} not found",
        )
    return food


# get all food items
@router.get("/", response_model=list[FoodResponse])
async def get_all_foods(db: Session = Depends(get_db)) -> list[FoodResponse]:
    """Get all food items."""
    food_service = FoodService()
    return food_service.get_all_foods(db)


# put route - update food
@router.put("/{food_id}", response_model=FoodResponse)
async def update_food(
    food_id: int, food: FoodCreate, db: Session = Depends(get_db)
) -> FoodResponse:
    """Update an existing food by ID."""
    food_service = FoodService()
    updated_food = food_service.update_food_by_id(db, food_id, food.model_dump())
    if not updated_food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"food with ID {food_id} not found",
        )
    return updated_food


# delete route - delete food
@router.delete("/{food_id}", response_model=FoodResponse)
async def delete_food(food_id: int, db: Session = Depends(get_db)) -> FoodResponse:
    """Delete an existing food by ID."""
    food_service = FoodService()
    deleted_food = food_service.delete_food_by_id(db, food_id)
    if not deleted_food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"food with ID {food_id} not found",
        )
    return deleted_food