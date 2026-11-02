import pytest
from pydantic import ValidationError

from schemas.calendar import CalendarDayRequest, CalendarDaySummary, CalendarMonthRequest


class TestCalendarMonthRequest:
    def test_valid_request(self):
        req = CalendarMonthRequest(month="2026-10", timezone="America/New_York")
        assert req.month == "2026-10"
        assert req.timezone == "America/New_York"

    def test_invalid_month_format(self):
        with pytest.raises(ValidationError):
            CalendarMonthRequest(month="2026-13", timezone="America/New_York")

    def test_invalid_month_not_numeric(self):
        with pytest.raises(ValidationError):
            CalendarMonthRequest(month="abcd-ef", timezone="America/New_York")

    def test_invalid_month_single_part(self):
        with pytest.raises(ValidationError):
            CalendarMonthRequest(month="202610", timezone="America/New_York")

    def test_invalid_timezone(self):
        with pytest.raises(ValidationError):
            CalendarMonthRequest(month="2026-10", timezone="Not/A/Timezone")

    def test_year_out_of_range(self):
        with pytest.raises(ValidationError):
            CalendarMonthRequest(month="1999-10", timezone="UTC")


class TestCalendarDaySummary:
    def test_valid_summary(self):
        summary = CalendarDaySummary(
            date="2026-10-01",
            food_count=3,
            symptom_count=1,
            health_synced=True,
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


class TestCalendarDayRequest:
    def test_valid_request(self):
        req = CalendarDayRequest(date="2026-10-05", timezone="America/New_York")
        assert req.timezone == "America/New_York"

    def test_invalid_timezone(self):
        with pytest.raises(ValidationError):
            CalendarDayRequest(date="2026-10-05", timezone="Fake/Zone")

    def test_invalid_date(self):
        with pytest.raises(ValidationError):
            CalendarDayRequest(date="not-a-date", timezone="UTC")
