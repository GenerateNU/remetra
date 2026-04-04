"""Food log Pydantic schemas for request/response validation."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FoodLogBase(BaseModel):
    """Common food log fields."""

    food_id: uuid.UUID = Field(..., description="ID of the food being logged")
    quantity: Optional[str] = Field(
        default=None,
        description="Quantity consumed e.g. '1 cup', '2 slices'",
    )
    timestamp: datetime = Field(..., description="When the food was consumed")
    notes: Optional[str] = Field(default=None, description="Optional notes")


class FoodLogCreate(FoodLogBase):
    """Schema for creating a food log entry."""

    username: str = Field(..., description="Username of the user logging the food")


class FoodLogResponse(FoodLogBase):
    """Schema for returning a food log entry."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Unique ID for this food log entry")
    username: str
    created_at: datetime
