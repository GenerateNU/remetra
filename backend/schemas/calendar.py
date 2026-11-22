from datetime import date

from pydantic import BaseModel, Field

from schemas.food_log import FoodLogResponse
from schemas.symptom_log import SymptomLogResponse


class CalendarDaySummary(BaseModel):
    date: date
    food_count: int = Field(0, ge=0)
    symptom_count: int = Field(0, ge=0)
    has_health_data: bool = False
    status: str = Field(..., description="complete | food_only | symptoms_only | empty")


class CalendarMonthResponse(BaseModel):
    month: str = Field(..., description="YYYY-MM")
    days: list[CalendarDaySummary]
    current_streak: int = Field(0, ge=0)
    longest_streak: int = Field(0, ge=0)


class CalendarDayResponse(BaseModel):
    date: date
    food_logs: list[FoodLogResponse]
    symptom_logs: list[SymptomLogResponse]
