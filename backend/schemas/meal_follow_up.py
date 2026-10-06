"""Meal follow up Pydantic schemas for request/response validation."""

from uuid import UUID
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

# returns the notification details: when to send it, the message, where tapping it should go 

class MealFollowUpResponse(BaseModel):
    """Schema for returning a meal follow up entry."""
    class Data(BaseModel):
        log_type: Literal["symptom"] = Field(default=None, description="Type of log")
        food_log_id:UUID = Field(default=None, description="ID of food log")

    should_schedule: bool = Field(default=False, description="If true, the notification should be scheduled") 
    fire_at: datetime = Field(..., description="When to send the notification")
    title: str = Field(default=None, description="Notification title")
    body: str = Field(default=None, description="Notifcation body")  
    data: Data  
    

    
    

