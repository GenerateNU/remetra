from unittest.mock import MagicMock, patch

from schemas.health import HealthDayEntry, HealthEventEntry, HealthSyncRequest, HealthSyncResponse
from services.health_sync_service import HealthSyncService


VALID_DAY = {
    "date": "2026-09-28",
    "sleep_total_min": 412,
    "sleep_deep_min": 58,
    "sleep_rem_min": 91,
    "sleep_core_min": 263,
    "sleep_awake_min": 24,
    "hrv_avg_ms": 40.4,
    "resting_hr_bpm": 61,
}

VALID_EVENT = {
    "hk_uuid": "8F2A1C3E-4B5D-4E6F-9A0B-1C2D3E4F5A6B",
    "category": "symptom",
    "type": "fatigue",
    "value": "moderate",
    "start_at": "2026-09-28T14:00:00Z",
    "end_at": "2026-09-28T18:00:00Z",
    "date": "2026-09-28",
}


def _make_request(days=None, events=None):
    return HealthSyncRequest(
        timezone="America/New_York",
        days=[HealthDayEntry(**d) for d in (days or [])],
        events=[HealthEventEntry(**e) for e in (events or [])],
    )


class TestHealthSyncService:
    def test_sync_returns_correct_counts(self):
        with patch("services.health_sync_service.HealthRepository") as MockRepo:
            MockRepo.return_value.save_days.return_value = 1
            MockRepo.return_value.save_events.return_value = 1
            request = _make_request(days=[VALID_DAY], events=[VALID_EVENT])
            result = HealthSyncService().sync(db=MagicMock(), username="alice", request=request)
        assert isinstance(result, HealthSyncResponse)
        assert result.days_saved == 1
        assert result.events_added == 1
        assert result.events_skipped == 0

    def test_sync_calculates_events_skipped(self):
        with patch("services.health_sync_service.HealthRepository") as MockRepo:
            MockRepo.return_value.save_days.return_value = 0
            MockRepo.return_value.save_events.return_value = 1
            second_event = {**VALID_EVENT, "hk_uuid": "AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE"}
            request = _make_request(events=[VALID_EVENT, second_event])
            result = HealthSyncService().sync(db=MagicMock(), username="alice", request=request)
        assert result.events_added == 1
        assert result.events_skipped == 1

    def test_sync_with_empty_days_and_events(self):
        with patch("services.health_sync_service.HealthRepository") as MockRepo:
            MockRepo.return_value.save_days.return_value = 0
            MockRepo.return_value.save_events.return_value = 0
            request = _make_request()
            result = HealthSyncService().sync(db=MagicMock(), username="alice", request=request)
        assert result.days_saved == 0
        assert result.events_added == 0
        assert result.events_skipped == 0
