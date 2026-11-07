from datetime import UTC, date, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from services.health_trends_service import HealthTrendsService


def _make_health_row(day, sleep=420, hrv=50.0, hr=60.0, timezone="America/New_York"):
    return SimpleNamespace(
        date=day, sleep_total_min=sleep, hrv_avg_ms=hrv, resting_hr_bpm=hr, timezone=timezone
    )


def _make_symptom_log(timestamp, intensity):
    return SimpleNamespace(timestamp=timestamp, intensity=intensity)


def _get_trends(start, end, health_rows=None, symptom_logs=None):
    with patch("services.health_trends_service.HealthRepository") as MockRepo:
        MockRepo.return_value.get_days_in_range.return_value = health_rows or []
        MockRepo.return_value.get_symptom_logs_in_range.return_value = symptom_logs or []
        return HealthTrendsService().get_trends(db=MagicMock(), username="alice", start=start, end=end)


class TestHealthTrendsService:
    def test_seven_day_range_with_three_data_days(self):
        health_rows = [
            _make_health_row(date(2026, 10, 20)),
            _make_health_row(date(2026, 10, 22)),
            _make_health_row(date(2026, 10, 25)),

        ]
        trends = _get_trends(date(2026, 10, 20), date(2026, 10, 26), health_rows=health_rows)
        assert len(trends) == 7
        assert [day.date for day in trends] == [date(2026, 10, d) for d in range(20, 27)]
        null_days = [day for day in trends if day.sleep_total_min is None]
        assert len(null_days) == 4
        for day in null_days:
            assert day.hrv_avg_ms is None
            assert day.resting_hr_bpm is None


    def test_two_symptoms_on_one_day(self):
        symptom_logs = [
            _make_symptom_log(datetime(2026, 10, 20, 14, 0, tzinfo=UTC), 3),
            _make_symptom_log(datetime(2026, 10, 20, 18, 0, tzinfo=UTC), 6),
        ]
        trends = _get_trends(date(2026, 10, 20), date(2026, 10, 20), symptom_logs=symptom_logs)
        assert trends[0].symptom_count == 2
        assert trends[0].max_intensity == 6


    def test_day_no_symptoms_has_zero_count_and_null_intensity(self):
        health_rows = [_make_health_row(date(2026, 10, 20))]
        trends = _get_trends(date(2026, 10, 20), date(2026, 10, 20), health_rows=health_rows)
        assert trends[0].symptom_count == 0
        assert trends[0].max_intensity is None
        assert trends[0].sleep_total_min == 420


    def test_symptoms_grouped_by_users_local_date(self):
        health_rows = [_make_health_row(date(2026, 10, 20))]
        symptom_logs = [_make_symptom_log(datetime(2026, 10, 21, 2, 0, tzinfo=UTC), 4)]
        trends = _get_trends(
            date(2026, 10, 20), date(2026, 10, 21), health_rows=health_rows, symptom_logs=symptom_logs
        )
        assert trends[0].symptom_count == 1
        assert trends[1].symptom_count == 0


    def test_falls_back_to_utc_without_health_rows(self):
        symptom_logs = [_make_symptom_log(datetime(2026, 10, 21, 2, 0, tzinfo=UTC), 4)]
        trends = _get_trends(date(2026, 10, 20), date(2026, 10, 21), symptom_logs=symptom_logs)
        assert trends[0].symptom_count == 0
        assert trends[1].symptom_count == 1


    def test_symptoms_outside_range_are_dropped(self):
        symptom_logs = [_make_symptom_log(datetime(2026, 10, 19, 12, 0, tzinfo=UTC), 5)]
        trends = _get_trends(date(2026, 10, 20), date(2026, 10, 20), symptom_logs=symptom_logs)
        assert trends[0].symptom_count == 0
