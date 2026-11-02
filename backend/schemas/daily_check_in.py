from datetime import date, datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, model_validator

MAX_CHECK_IN_DAYS_BACK = 7


class DailyCheckInCreate(BaseModel):
    """Schema for a 'no symptoms' check-in. Owner is the signed-in user."""

    date: date
    timezone: str = Field(..., description="Device timezone, e.g. America/New_York")

    @model_validator(mode="after")
    def validate_date_and_timezone(self):
        try:
            tz = ZoneInfo(self.timezone)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError(f"'{self.timezone}' is not a valid timezone") from None

        today = datetime.now(tz).date()
        if self.date > today:
            raise ValueError("date cannot be in the future")
        if self.date < today - timedelta(days=MAX_CHECK_IN_DAYS_BACK):
            raise ValueError(f"date cannot be more than {MAX_CHECK_IN_DAYS_BACK} days ago")
        return self


class DailyCheckInResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique ID for this check-in")
    username: str = Field(..., description="Username")
    date: date
    timezone: str = Field(..., description="Timezone the check-in was made in")
    created_at: datetime = Field(..., description="When this check-in was created")