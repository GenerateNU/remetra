"""Pydantic schemas for tags."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TagBase(BaseModel):
    """Shared tag fields."""
    name: str
    description: Optional[str] = None
    is_system: bool = False


class TagCreate(TagBase):
    """Schema for creating a tag."""
    pass


class TagResponse(TagBase):
    """Schema for returning a tag."""
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SuggestedIngredientResponse(BaseModel):
    """Schema for an LLM-suggested ingredient with its trigger buckets."""
    name: str
    buckets: list[str]


class SuggestedBucketResponse(BaseModel):
    """Schema for a suggested trigger bucket tag."""
    name: str
    description: Optional[str] = None


class SuggestedTagsAndIngredientsResponse(BaseModel):
    """Schema for the full LLM suggestion response."""
    suggested_ingredients: list[SuggestedIngredientResponse]
    suggested_buckets: list[SuggestedBucketResponse]

class FoodSuggestionRequest(BaseModel):
    """
    Request schema for pre-create food suggestions.
    Accepts draft food info and optional pre-selected tags,
    returns LLM/RAG suggested ingredients and buckets without persisting anything.
    """
    name: str = Field(..., description="Name of the food", min_length=1, max_length=100)
    ingredients: list[str] = Field(default=[], description="List of ingredients already known")
    selected_tag_ids: list[UUID] = Field(default=[], description="Tag IDs the user already selected")