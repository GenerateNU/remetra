from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

 
class SymptomLog(BaseModel):
    """Shared fields for symptom log requests and responses."""

    symptom_id: int = Field(..., description="ID of the associated symptom")
    intensity: int = Field(..., description="Intensity of the symptom", ge=1, le=10)
    timestamp: datetime = Field(..., description="When the symptom occurred")
    duration: Optional[int] = Field(None, description="Duration in minutes", ge=0)
    notes: Optional[str] = Field(None, description="Additional notes about the symptom")


class SymptomLogCreate(SymptomLog):
    """
    Data structure for creating a new symptom log.
    
    Inherits all fields from SymptomLog base class.
    """
    username: str = Field(..., description="Username of the person logging the symptom")



class SymptomLogResponse(SymptomLog):
    """
    Data structure for symptom log responses sent back to clients.
    
    Includes the original symptom log data plus ID and timestamps 
    that the database generates automatically.
    """
    
    model_config = ConfigDict(from_attributes=True) 
    
    id: int = Field(..., description="Unique ID for this symptom log")
    username: str = Field(..., description="Username")
    created_at: datetime = Field(..., description="When this log was created")