from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

class symptom_log(BaseModel):
    """
    Data structure for chocolate responses sent back to clients.

    Includes the original chocolate data plus new fields
    like ID, timestamps, and current stock that the database tracks automatically.
    """

    model_config = ConfigDict(from_attributes=True)  # Allows loading from database models (SQLAlchemy)

    log_id: int = Field(..., description="Unique ID for the symptom log")
    symptom_id: int = Field(..., description="ID of the symptom")
    intesity: int = Field(..., description="Intensity of the symptom")
    timestamp: datetime = Field(..., description="When the symptom appeared")
    duration: Optional[int] = Field(None, description="Duration of the symptom in minutes")
    
