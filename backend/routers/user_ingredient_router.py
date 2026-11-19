"""
Router for user's ingredient preference endpoints.

Handles reading and replacing the ingredients a user wants to avoid, suspects, or considers safe for them to eat.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_user
from schemas.user import UserIngredientsResponse, UserIngredientsUpdate, UserResponse
from services.user_ingredient_service import UserIngredientService

router = APIRouter(
    prefix="/users",
    tags=["User_Ingredients"],
)


@router.get(
    "/me/ingredients",
    response_model=UserIngredientsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_my_ingredients(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> UserIngredientsResponse:
    """Get the user's ingredients grouped by their preferences."""
    return UserIngredientService().get_ingredients(db, current_user.username)


@router.put(
    "/me/ingredients",
    response_model=UserIngredientsResponse,
    status_code=status.HTTP_200_OK,
)
async def replace_my_ingredients(
    payload: UserIngredientsUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> UserIngredientsResponse:
    """Replace the user's whole set of ingredient preferences."""
    try:
        return UserIngredientService().replace_ingredients(db, current_user.username, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))