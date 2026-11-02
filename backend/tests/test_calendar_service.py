from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from schemas.calendar import CalendarDayRequest, CalendarMonthRequest, CalendarMonthResponse
from services.calendar_service import CalendarService, _compute_streaks, _day_status


class TestDayStatus:
    def test_complete(self):
        assert _day_status(2, 1) == "complete"

    def test_food_only(self):
        assert _day_status(3, 0) == "food_only"

    def test_symptoms_only(self):
        assert _day_status(0, 2) == "symptoms_only"

    def test_empty(self):
        assert _day_status(0, 0) == "empty"


class TestComputeStreaks:
    def test_empty(self):
        assert _compute_streaks(set()) == (0, 0)

    def test_single_day_today(self):
        today = date.today()
        current, longest = _compute_streaks({today})
        assert current == 1
        assert longest == 1

    def test_single_day_in_past(self):
        past = date(2026, 1, 15)
        current, longest = _compute_streaks({past})
        assert current == 0
        assert longest == 1

    def test_consecutive_streak(self):
        today = date.today()
        dates = {today - timedelta(days=i) for i in range(5)}
        current, longest = _compute_streaks(dates)
        assert current == 5
        assert longest == 5

    def test_longest_streak_in_past(self):
        dates = {date(2026, 3, d) for d in range(1, 11)}
        current, longest = _compute_streaks(dates)
        assert current == 0
        assert longest == 10

    def test_gap_breaks_streak(self):
        today = date.today()
        dates = {today, today - timedelta(days=1), today - timedelta(days=3), today - timedelta(days=4)}
        current, longest = _compute_streaks(dates)
        assert current == 2
        assert longest == 2

    def test_yesterday_fallback_when_today_not_logged(self):
        yesterday = date.today() - timedelta(days=1)
        dates = {yesterday, yesterday - timedelta(days=1), yesterday - timedelta(days=2)}
        current, longest = _compute_streaks(dates)
        assert current == 3
        assert longest == 3

    def test_streak_across_month_boundary(self):
        dates = {date(2026, 10, 30), date(2026, 10, 31), date(2026, 11, 1)}
        _, longest = _compute_streaks(dates)
        assert longest == 3


class TestCalendarServiceMonth:
    def _make_request(self, month="2026-10", tz="America/New_York"):
        return CalendarMonthRequest(month=month, timezone=tz)

    @patch("services.calendar_service.CalendarRepository")
    def test_returns_all_days_in_month(self, MockRepo):
        MockRepo.return_value.get_food_counts.return_value = {}
        MockRepo.return_value.get_symptom_counts.return_value = {}
        MockRepo.return_value.get_health_synced_dates.return_value = set()
        MockRepo.return_value.get_all_logged_dates.return_value = set()

        result = CalendarService().get_month(MagicMock(), "alice", self._make_request())
        assert isinstance(result, CalendarMonthResponse)
        assert len(result.days) == 31
        assert result.days[0].date == date(2026, 10, 1)
        assert result.days[-1].date == date(2026, 10, 31)

    @patch("services.calendar_service.CalendarRepository")
    def test_february_has_28_days(self, MockRepo):
        MockRepo.return_value.get_food_counts.return_value = {}
        MockRepo.return_value.get_symptom_counts.return_value = {}
        MockRepo.return_value.get_health_synced_dates.return_value = set()
        MockRepo.return_value.get_all_logged_dates.return_value = set()

        result = CalendarService().get_month(MagicMock(), "alice", self._make_request(month="2026-02"))
        assert len(result.days) == 28

    @patch("services.calendar_service.CalendarRepository")
    def test_day_statuses_assigned_correctly(self, MockRepo):
        MockRepo.return_value.get_food_counts.return_value = {
            date(2026, 10, 1): 3,
            date(2026, 10, 2): 1,
        }
        MockRepo.return_value.get_symptom_counts.return_value = {
            date(2026, 10, 1): 2,
            date(2026, 10, 3): 1,
        }
        MockRepo.return_value.get_health_synced_dates.return_value = {date(2026, 10, 1)}
        MockRepo.return_value.get_all_logged_dates.return_value = set()

        result = CalendarService().get_month(MagicMock(), "alice", self._make_request())

        day1 = result.days[0]
        assert day1.status == "complete"
        assert day1.food_count == 3
        assert day1.symptom_count == 2
        assert day1.health_synced is True

        day2 = result.days[1]
        assert day2.status == "food_only"

        day3 = result.days[2]
        assert day3.status == "symptoms_only"

        day4 = result.days[3]
        assert day4.status == "empty"
        assert day4.health_synced is False

    @patch("services.calendar_service.CalendarRepository")
    def test_streaks_populated(self, MockRepo):
        today = date.today()
        MockRepo.return_value.get_food_counts.return_value = {}
        MockRepo.return_value.get_symptom_counts.return_value = {}
        MockRepo.return_value.get_health_synced_dates.return_value = set()
        MockRepo.return_value.get_all_logged_dates.return_value = {
            today,
            today - timedelta(days=1),
        }

        result = CalendarService().get_month(MagicMock(), "alice", self._make_request())
        assert result.current_streak == 2
        assert result.longest_streak == 2

    @patch("services.calendar_service.CalendarRepository")
    def test_queries_scoped_to_username(self, MockRepo):
        mock_repo = MockRepo.return_value
        mock_repo.get_food_counts.return_value = {}
        mock_repo.get_symptom_counts.return_value = {}
        mock_repo.get_health_synced_dates.return_value = set()
        mock_repo.get_all_logged_dates.return_value = set()

        db = MagicMock()
        CalendarService().get_month(db, "alice", self._make_request())

        for call in mock_repo.get_food_counts.call_args_list:
            assert call[0][1] == "alice"
        for call in mock_repo.get_symptom_counts.call_args_list:
            assert call[0][1] == "alice"
        for call in mock_repo.get_health_synced_dates.call_args_list:
            assert call[0][1] == "alice"
        for call in mock_repo.get_all_logged_dates.call_args_list:
            assert call[0][1] == "alice"


class TestCalendarServiceDay:
    @patch("services.calendar_service.CalendarRepository")
    def test_get_day_returns_logs(self, MockRepo):
        mock_food = MagicMock()
        mock_food.id = "00000000-0000-0000-0000-000000000001"
        mock_food.food_id = "00000000-0000-0000-0000-000000000010"
        mock_food.username = "alice"
        mock_food.quantity = "1 cup"
        mock_food.timestamp = "2026-10-05T12:00:00Z"
        mock_food.notes = None
        mock_food.created_at = "2026-10-05T12:00:00Z"

        mock_symptom = MagicMock()
        mock_symptom.id = "00000000-0000-0000-0000-000000000002"
        mock_symptom.symptom_id = "00000000-0000-0000-0000-000000000020"
        mock_symptom.username = "alice"
        mock_symptom.intensity = 5
        mock_symptom.timestamp = "2026-10-05T14:00:00Z"
        mock_symptom.duration = 30
        mock_symptom.notes = None
        mock_symptom.created_at = "2026-10-05T14:00:00Z"

        MockRepo.return_value.get_food_logs_for_day.return_value = [mock_food]
        MockRepo.return_value.get_symptom_logs_for_day.return_value = [mock_symptom]

        request = CalendarDayRequest(date="2026-10-05", timezone="America/New_York")
        result = CalendarService().get_day(MagicMock(), "alice", request)

        assert result.date == date(2026, 10, 5)
        assert len(result.food_logs) == 1
        assert len(result.symptom_logs) == 1

    @patch("services.calendar_service.CalendarRepository")
    def test_get_day_empty(self, MockRepo):
        MockRepo.return_value.get_food_logs_for_day.return_value = []
        MockRepo.return_value.get_symptom_logs_for_day.return_value = []

        request = CalendarDayRequest(date="2026-10-05", timezone="America/New_York")
        result = CalendarService().get_day(MagicMock(), "alice", request)

        assert result.date == date(2026, 10, 5)
        assert len(result.food_logs) == 0
        assert len(result.symptom_logs) == 0

    @patch("services.calendar_service.CalendarRepository")
    def test_get_day_scoped_to_username(self, MockRepo):
        mock_repo = MockRepo.return_value
        mock_repo.get_food_logs_for_day.return_value = []
        mock_repo.get_symptom_logs_for_day.return_value = []

        db = MagicMock()
        request = CalendarDayRequest(date="2026-10-05", timezone="America/New_York")
        CalendarService().get_day(db, "alice", request)

        assert mock_repo.get_food_logs_for_day.call_args[0][1] == "alice"
        assert mock_repo.get_symptom_logs_for_day.call_args[0][1] == "alice"
