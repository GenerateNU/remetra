"""Response schema for the daily ingredient pool."""

from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class IngredientPoolResponse(BaseModel):
    """
    Today's ingredient pool as shown to the user.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    pool_date: date
    ingredients: list[str]
