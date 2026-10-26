from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

SYMPTOM_VALUES = {"mild", "moderate", "severe"}
FLOW_VALUES = {"light", "medium", "heavy"}
VALID_CATEGORIES = {"symptom", "menstrual_flow"}


class HealthDayEntry(BaseModel):
    date: date
    sleep_total_min: Optional[int] = Field(None, ge=0, le=1440, description="Total sleep in minutes")
    sleep_deep_min: Optional[int] = Field(None, ge=0, le=1440, description="Deep sleep in minutes")
    sleep_rem_min: Optional[int] = Field(None, ge=0, le=1440, description="REM sleep in minutes")
    sleep_core_min: Optional[int] = Field(None, ge=0, le=1440, description="Core sleep in minutes")
    sleep_awake_min: Optional[int] = Field(None, ge=0, le=1440, description="Awake time in minutes")
    hrv_avg_ms: Optional[float] = Field(None, description="Average heart rate variability in ms")
    resting_hr_bpm: Optional[float] = Field(None, description="Resting heart rate in bpm")


class HealthEventEntry(BaseModel):
    hk_uuid: UUID = Field(..., description="Apple Health unique event ID")
    category: str = Field(..., description="Event category: symptom or menstrual_flow")
    type: str = Field(..., description="Event type, e.g. headache, fatigue, bloating")
    value: str = Field(..., description="Severity or flow level")
    start_at: datetime = Field(..., description="Event start time")
    end_at: datetime = Field(..., description="Event end time")
    date: date

    @model_validator(mode="after")
    def validate_category_and_value(self):
        if self.category not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of {VALID_CATEGORIES}, got '{self.category}'")
        if self.category == "symptom" and self.value not in SYMPTOM_VALUES:
            raise ValueError(f"symptom value must be one of {SYMPTOM_VALUES}, got '{self.value}'")
        if self.category == "menstrual_flow" and self.value not in FLOW_VALUES:
            raise ValueError(f"menstrual_flow value must be one of {FLOW_VALUES}, got '{self.value}'")
        return self


class HealthSyncRequest(BaseModel):
    timezone: str = Field(..., description="Client timezone, e.g. America/New_York")
    days: list[HealthDayEntry] = Field(..., description="Daily health metric entries")
    events: list[HealthEventEntry] = Field(..., description="Discrete health events")


class HealthSyncResponse(BaseModel):
    days_saved: int = Field(..., description="Number of days inserted or updated")
    events_added: int = Field(..., description="Number of new events inserted")
    events_skipped: int = Field(..., description="Number of duplicate events skipped")

class HealthTrendDay(BaseModel):
    date: date
    sleep_total_min: Optional[int] = Field(None, description="Total sleep in minutes, null if no data that day")
    hrv_avg_ms: Optional[float] = Field(None, description="Average heart rate variability in ms, null if no data")
    resting_hr_bpm: Optional[float] = Field(None, description="Restng heart rate in bpm, null if no data")
    symptom_count: int = Field(0, ge=0, description="Number of symptom logs that day")
    max_intensity: Optional[int] = Field(None, description="Highest symptom intensity that day, null if no symptoms")