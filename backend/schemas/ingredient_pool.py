from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class IngredientPoolResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    pool_date: date
    ingredient_ids: list[str]
