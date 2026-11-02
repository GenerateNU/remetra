from datetime import date
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, Field, field_validator

from schemas.food_log import FoodLogResponse
from schemas.symptom_log import SymptomLogResponse


class CalendarDaySummary(BaseModel):
    date: date
    food_count: int = Field(0, ge=0)
    symptom_count: int = Field(0, ge=0)
    health_synced: bool = False
    status: str = Field(..., description="complete | food_only | symptoms_only | empty")


class CalendarMonthResponse(BaseModel):
    days: list[CalendarDaySummary]
    current_streak: int = Field(0, ge=0)
    longest_streak: int = Field(0, ge=0)


class CalendarMonthRequest(BaseModel):
    month: str = Field(..., description="Month in YYYY-MM format, e.g. 2026-10")
    timezone: str = Field(..., description="IANA timezone, e.g. America/New_York")

    @field_validator("month")
    @classmethod
    def validate_month(cls, v: str) -> str:
        parts = v.split("-")
        if len(parts) != 2:
            raise ValueError("month must be YYYY-MM format")
        year, month = parts
        if not year.isdigit() or not month.isdigit():
            raise ValueError("month must be YYYY-MM format")
        if not 1 <= int(month) <= 12:
            raise ValueError("month must be between 01 and 12")
        if int(year) < 2000 or int(year) > 2100:
            raise ValueError("year must be between 2000 and 2100")
        return v

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        try:
            ZoneInfo(v)
        except (ZoneInfoNotFoundError, KeyError):
            raise ValueError(f"invalid timezone: {v}")
        return v


class CalendarDayRequest(BaseModel):
    date: date
    timezone: str = Field(..., description="IANA timezone, e.g. America/New_York")

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        try:
            ZoneInfo(v)
        except (ZoneInfoNotFoundError, KeyError):
            raise ValueError(f"invalid timezone: {v}")
        return v


class CalendarDayResponse(BaseModel):
    date: date
    food_logs: list[FoodLogResponse]
    symptom_logs: list[SymptomLogResponse]
