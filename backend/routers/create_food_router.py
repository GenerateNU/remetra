from typing import List, Optional

from fastapi import APIRouter, HTTPException, status

from examples.example_pydantic_models import (
    CreateFoodErrorResponse,
    CreateFoodResponse,
    FoodCreate,
)
from services.food_service_layer import FoodService

food_service = FoodService()

router = APIRouter(
    prefix="/createFood",
    tags=["Create food"],
)


@router.post(
    "/",
    response_model=CreateFoodResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": CreateFoodErrorResponse, "description": "Invalid food data"},
    },
)
async def create_food(food: FoodCreate) -> CreateFoodResponse:
    try:
        food_dict = food.model_dump()

        created = await food_service.create_food(food_dict)
        return created

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/",
    response_model=List[CreateFoodResponse],
    responses={200: {"description": "List of foods"}},
)
async def get_foods(
    name: str,
    id: int,
    ingredients: List[str],
) -> List[CreateFoodResponse]:
    foods = await food_service.get_foods(name=name, id=id, ingredients=ingredients)
    return foods


@router.get(
    "/{food_id}",
    response_model=CreateFoodResponse,
    responses={400: {"model": CreateFoodErrorResponse, "description": "Food not found"}},
)
async def get_food(
    id: int,
) -> CreateFoodResponse:
    food = await food_service.get_by_food_id(id)
    if not food:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"Food with ID {food_id} not found"})

    return food


@router.put(
    "/",
    response_model=CreateFoodResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": CreateFoodErrorResponse, "description": "Invalid food data"},
    },
)
async def update_food(
    id: int, name: Optional[str] = None, ingredients: Optional[List[str]] = None
) -> CreateFoodResponse:
    try:
        food = await food_service.update_food(id=id, name=name, ingredients=ingredients)

        return food

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/",
    response_model=CreateFoodResponse,
    responses={400: {"model": CreateFoodErrorResponse, "description": "Food not found"}},
)
async def delete_food(
    id: int,
) -> CreateFoodResponse:
    food = await food_service.delete_food(id)
    if not food:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"Food with ID {food_id} not found"})
