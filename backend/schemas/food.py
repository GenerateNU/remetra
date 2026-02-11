"""User Pydantic schemas for request/response validation."""

import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FoodBase(BaseModel):
    """
    Common food fields used in both requests and responses.
    """

    name: str = Field(
        ...,  # by adding ... you make it a required field
        description="Name of the food",
        min_length=1,
        max_length=100,
    )
    ingredients: list = Field(
        ...,
        description="List of ingredients in the food list",
        max_length=500,
    )
    username: Optional[str] = Field(
        description="The username associated with a user-specific food",
        default=None,
    )


class FoodCreate(FoodBase):
    """
    Data structure for creating a new food product

    Used when a client sends a POST request to add a new food to inventory.
    Inherits all fields from FoodBase
    """


class FoodResponse(FoodBase):
    """
    Data structure for food responses sent back to clients.

    Includes food data
    like ID, timestamps, and current stock that the database tracks automatically.
    """

    model_config = ConfigDict(from_attributes=True)  # Allows loading from database models (SQLAlchemy)

    id: uuid.UUID = Field(..., description="Unique ID for this food product")
