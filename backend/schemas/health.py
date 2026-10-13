from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

SYMPTOM_VALUES = {"mild", "moderate", "severe"}
FLOW_VALUES = {"light", "medium", "heavy"}
VALID_CATEGORIES = {"symptom", "menstrual_flow"}


class HealthDayEntry(BaseModel):
    date: date
    sleep_total_min: Optional[int] = Field(None, ge=0, le=1440)
    sleep_deep_min: Optional[int] = Field(None, ge=0, le=1440)
    sleep_rem_min: Optional[int] = Field(None, ge=0, le=1440)
    sleep_core_min: Optional[int] = Field(None, ge=0, le=1440)
    sleep_awake_min: Optional[int] = Field(None, ge=0, le=1440)
    hrv_avg_ms: Optional[float] = None
    resting_hr_bpm: Optional[float] = None


class HealthEventEntry(BaseModel):
    hk_uuid: UUID
    category: str
    type: str
    value: str
    start_at: datetime
    end_at: datetime
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
    timezone: str
    days: list[HealthDayEntry]
    events: list[HealthEventEntry]


class HealthSyncResponse(BaseModel):
    days_saved: int
    events_added: int
    events_skipped: int
