from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SymptomLogBase(BaseModel):
    symptom_id: UUID = Field(..., description="ID of the associated symptom")
    intensity: int = Field(..., description="Intensity of the symptom", ge=1, le=10)
    timestamp: datetime = Field(..., description="When the symptom occurred")
    duration: Optional[int] = Field(None, description="Duration in minutes", ge=0)
    notes: Optional[str] = Field(None, description="Additional notes about the symptom")


class SymptomLogCreate(SymptomLogBase):
    """Schema for creating a symptom log. The owner is the signed-in user."""


class SymptomLogUpdate(BaseModel):
    intensity: Optional[int] = Field(None, description="Intensity of the symptom", ge=1, le=10)
    timestamp: Optional[datetime] = Field(None, description="When the symptom occurred")
    duration: Optional[int] = Field(None, description="Duration in minutes", ge=0)
    notes: Optional[str] = Field(None, description="Additional notes about the symptom")


class SymptomLogResponse(SymptomLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique ID for this symptom log")
    username: str = Field(..., description="Username")
    created_at: datetime = Field(..., description="When this log was created")
