from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_user
from schemas.ingredient_pool import IngredientPoolResponse
from services.ingredient_pool_service import IngredientPoolService

router = APIRouter(
    prefix="/pool",
    tags=["Ingredient Pool"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/today", response_model=IngredientPoolResponse)
def get_today_pool(db: Session = Depends(get_db)) -> IngredientPoolResponse:
    """Get or create today's ingredient pool for the authenticated user."""
    return IngredientPoolService().get_today_pool(db)
