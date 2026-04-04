"""User Pydantic schemas for request/response validation."""

import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from schemas.tag import SuggestedBucketResponse, SuggestedIngredientResponse, TagResponse


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

    Includes food data like ID, timestamps, and current stock that the database tracks automatically.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Unique ID for this food product")
    tags: list[TagResponse] = Field(default=[], description="Confirmed trigger bucket tags for this food")
    suggested_ingredients: list[SuggestedIngredientResponse] = Field(
        default=[], description="LLM-suggested ingredients with their trigger buckets"
    )
    suggested_buckets: list[SuggestedBucketResponse] = Field(
        default=[], description="LLM-suggested trigger bucket tags for this food"
    )


class FoodSuggestionRequest(BaseModel):
    """
    Request schema for pre-create food suggestions.
    Accepts draft food info and optional pre-selected tags,
    returns LLM/RAG suggested ingredients and buckets without persisting anything.
    """

    name: str = Field(..., description="Name of the food", min_length=1, max_length=100)
    ingredients: list[str] = Field(default=[], description="List of ingredients already known")
    selected_tag_ids: list[uuid.UUID] = Field(default=[], description="Tag IDs the user already selected")
