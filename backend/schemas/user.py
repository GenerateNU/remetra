"""User Pydantic schemas for request/response validation."""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    dob: Optional[date] = None
    disease: Optional[list[str]] = None
    weight: Optional[float] = None
    gender: Optional[str] = None
    medication: Optional[list[str]] = None


class UserResponse(BaseModel):
    """Public user data (excludes password_hash). Not sure if this will be useful atm"""

    username: str
    email: str
    dob: Optional[date] = None
    disease: Optional[list[str]] = None
    weight: Optional[float] = None
    gender: Optional[str] = None
    medication: Optional[list[str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Allow conversion from ORM models (e.g., SQLAlchemy User) to Pydantic schema


class IngredientSummary(BaseModel):
    """An ingredient as shown in the user's preference lists."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    canonical_name: str


class UserIngredientsUpdate(BaseModel):
    """The user's full set of ingredient preferences. Replaces whatever was saved before."""

    avoid: list[UUID] = []
    suspect: list[UUID] = []
    safe: list[UUID] = []

    @model_validator(mode="after")
    def check_lists(self):
        self.avoid = list(dict.fromkeys(self.avoid))
        self.suspect = list(dict.fromkeys(self.suspect))
        self.safe = list(dict.fromkeys(self.safe))

        avoid, suspect, safe = set(self.avoid), set(self.suspect), set(self.safe)
        if (avoid & suspect) or (avoid & safe) or (suspect & safe):
            raise ValueError("Each ingredient can only be in one list")
        return self


class UserIngredientsResponse(BaseModel):
    """The user's ingredient preferences, grouped by category. All three lists are always present."""

    avoid: list[IngredientSummary] = []
    suspect: list[IngredientSummary] = []
    safe: list[IngredientSummary] = []
