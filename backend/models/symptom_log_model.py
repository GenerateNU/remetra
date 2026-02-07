from datetime import datetime                                                        
from typing import Optional                                                          
from pydantic import BaseModel, ConfigDict, Field


class SymptomLog(BaseModel):
    """Shared fields for symptom log requests and responses."""

    symptom_id: int = Field(..., description="ID of the associated symptom")
    intensity: int = Field(..., description="Intensity of the symptom", ge=1, le=10)
    timestamp: datetime = Field(..., description="When the symptom occurred")
    duration: Optional[int] = Field(None, description="Duration in minutes", ge=0)
