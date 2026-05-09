from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SymptomBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    location: str = Field(..., min_length=1, max_length=255)
    sensation: str = Field(..., min_length=1, max_length=255)
    username: Optional[str] = None


class SymptomCreate(SymptomBase):
    """
    Schema used when creating a new symptom.
    """

    pass


class SymptomUpdate(BaseModel):
    """
    Schema used when updating a symptom.
    All fields optional.
    """

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    location: Optional[str] = Field(default=None, min_length=1, max_length=255)
    sensation: Optional[str] = Field(default=None, min_length=1, max_length=255)
    username: Optional[str] = None


class SymptomResponse(SymptomBase):
    """
    Schema returned to client.
    """

    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class CreateSymptomErrorResponse(BaseModel):
    detail: str
