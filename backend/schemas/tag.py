"""Pydantic schemas for tags."""
from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TagBase(BaseModel):
    """Shared tag fields."""
    name: str
    description: Optional[str] = None
    llm_suggested: bool = False


class TagCreate(TagBase):
    """Schema for creating a tag."""
    pass


class TagResponse(TagBase):
    """Schema for returning a tag."""
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


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