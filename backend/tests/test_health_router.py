VALID_REQUEST = {
    "timezone": "America/New_York",
    "days": [
        {
            "date": "2026-09-28",
            "sleep_total_min": 412,
            "sleep_deep_min": 58,
            "sleep_rem_min": 91,
            "sleep_core_min": 263,
            "sleep_awake_min": 24,
            "hrv_avg_ms": 40.4,
            "resting_hr_bpm": 61,
        }
    ],
    "events": [
        {
            "hk_uuid": "8F2A1C3E-4B5D-4E6F-9A0B-1C2D3E4F5A6B",
            "category": "symptom",
            "type": "fatigue",
            "value": "moderate",
            "start_at": "2026-09-28T14:00:00Z",
            "end_at": "2026-09-28T18:00:00Z",
            "date": "2026-09-28",
        }
    ],
}


class TestHealthRouter:
    def test_unauthenticated_returns_401(self, test_client):
        response = test_client.post("/health/sync", json=VALID_REQUEST)
        assert response.status_code == 401

    def test_invalid_data_returns_422(self, test_client, authenticated_user):
        invalid = {
            "timezone": "America/New_York",
            "days": [],
            "events": [
                {
                    "hk_uuid": "bad",
                    "category": "banana",
                    "type": "x",
                    "value": "y",
                    "start_at": "x",
                    "end_at": "x",
                    "date": "x",
                }
            ],
        }
        response = test_client.post(
            "/health/sync",
            json=invalid,
        )
        assert response.status_code == 422

    def test_valid_request_returns_200(self, test_client, authenticated_user):
        response = test_client.post(
            "/health/sync",
            json=VALID_REQUEST,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["days_saved"] == 1
        assert data["events_added"] == 1
        assert data["events_skipped"] == 0

    def test_duplicate_request_skips_events(self, test_client, authenticated_user):
        test_client.post("/health/sync", json=VALID_REQUEST)
        response = test_client.post("/health/sync", json=VALID_REQUEST)
        data = response.json()
        assert data["days_saved"] == 1
        assert data["events_added"] == 0
        assert data["events_skipped"] == 1
