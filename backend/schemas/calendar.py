"""Logging calendar Pydantic schemas."""

import re
from datetime import date
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

from local_day import parse_timezone
from schemas.food_log import FoodLogResponse
from schemas.symptom_log import SymptomLogResponse

MONTH_PATTERN = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])$")

# complete = food and at least one symptom logged that day
DayStatus = Literal["complete", "food_only", "symptoms_only", "empty"]


def _check_month(value: str) -> str:
    match = MONTH_PATTERN.fullmatch(value)
    if not match or int(match.group(1)) < 1:
        raise ValueError("month must be YYYY-MM, e.g. 2026-10")
    return value


def _check_timezone(value: str) -> str:
    parse_timezone(value)
    return value


MonthKey = Annotated[str, AfterValidator(_check_month)]
TimezoneName = Annotated[str, AfterValidator(_check_timezone)]


class CalendarDayResponse(BaseModel):
    """How completely one local day was logged."""

    model_config = ConfigDict(from_attributes=True)

    date: date
    food_count: int = Field(..., ge=0)
    symptom_count: int = Field(..., ge=0)
    has_health_data: bool = Field(..., description="Whether Apple Health data synced for this day")
    status: DayStatus


class CalendarMonthResponse(BaseModel):
    """One entry per day of the month, plus streaks over the user's whole history."""

    model_config = ConfigDict(from_attributes=True)

    month: str = Field(..., description="YYYY-MM")
    days: list[CalendarDayResponse]
    current_streak: int = Field(..., ge=0, description="Consecutive logged days ending today, or yesterday")
    longest_streak: int = Field(..., ge=0, description="Longest run of consecutive logged days, all time")


class DayLogsResponse(BaseModel):
    """Every log on one local day, oldest first."""

    model_config = ConfigDict(from_attributes=True)

    date: date
    food_logs: list[FoodLogResponse]
    symptom_logs: list[SymptomLogResponse]
