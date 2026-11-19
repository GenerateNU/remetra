import pytest
from pydantic import ValidationError

from schemas.calendar import CalendarDaySummary


class TestCalendarDaySummary:
    def test_valid_summary(self):
        summary = CalendarDaySummary(
            date="2026-10-01",
            food_count=3,
            symptom_count=1,
            has_health_data=True,
            status="complete",
        )
        assert summary.food_count == 3

    def test_negative_count_rejected(self):
        with pytest.raises(ValidationError):
            CalendarDaySummary(
                date="2026-10-01",
                food_count=-1,
                symptom_count=0,
                status="empty",
            )
