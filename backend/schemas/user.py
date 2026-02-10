"""User Pydantic schemas for request/response validation."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Schema for user registration."""

    username: str
    email: EmailStr
    password: str
    dob: Optional[date] = None
    disease: Optional[list[str]] = None
    weight: Optional[float] = None


class UserResponse(BaseModel):
    """Public user data (excludes password_hash). Not sure if this will be useful atm"""

    username: str
    email: str
    dob: Optional[date] = None
    disease: Optional[list[str]] = None
    weight: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True  # Allow conversion from ORM models (e.g., SQLAlchemy User) to Pydantic schema
