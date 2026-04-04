"""Unit tests for AlgorithmService."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from analysis.models import IngredientSymptomMetrics
from models.food_log import FoodLog
from models.metrics import Metrics
from models.symptom_log import SymptomLog
from schemas.algorithm import AlgorithmAssociationResponse, AlgorithmRunRequest
from services.algorithm_service import AlgorithmService


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _food_log(username="alice", food_id=None, timestamp="2024-01-01T08:00:00") -> FoodLog:
    log = FoodLog()
    log.id = uuid4()
    log.username = username
    log.food_id = food_id or uuid4()
    log.timestamp = _dt(timestamp)
    return log


def _symptom_log(username="alice", symptom_id=None, intensity=5, timestamp="2024-01-01T10:00:00") -> SymptomLog:
    log = SymptomLog()
    log.id = uuid4()
    log.username = username
    log.symptom_id = symptom_id or uuid4()
    log.intensity = intensity
    log.timestamp = _dt(timestamp)
    return log


def _metrics_row(username="alice", symptom_id=None, ingredient=None, **overrides) -> Metrics:
    row = Metrics()
    row.id = uuid4()
    row.username = username
    row.symptom_id = symptom_id or uuid4()
    row.ingredient = str(ingredient or uuid4())
    row.exposures = overrides.get("exposures", 1)
    row.trigger_rate = overrides.get("trigger_rate", 0.5)
    row.base_rate = overrides.get("base_rate", 0.2)
    row.fishers_p_value = overrides.get("fishers_p_value", 0.05)
    row.average_intensity = overrides.get("average_intensity", 5.0)
    row.updated_at = overrides.get("updated_at", datetime(2024, 1, 1, tzinfo=timezone.utc))
    return row


# ---------------------------------------------------------------------------
# _build_metrics_by_symptom
# ---------------------------------------------------------------------------


class TestBuildMetricsBySymptom:
    def test_returns_empty_dict_when_no_food_logs(self):
        service = AlgorithmService()
        result = service._build_metrics_by_symptom(
            food_logs=[], symptom_logs=[_symptom_log()], time_window_hours=4.0
        )
        assert result == {}

    def test_returns_empty_dict_when_no_symptom_logs(self):
        service = AlgorithmService()
        result = service._build_metrics_by_symptom(
            food_logs=[_food_log()], symptom_logs=[], time_window_hours=4.0
        )
        assert result == {}

    def test_returns_empty_dict_when_both_empty(self):
        service = AlgorithmService()
        assert service._build_metrics_by_symptom(food_logs=[], symptom_logs=[], time_window_hours=4.0) == {}

    def test_raises_for_negative_time_window(self):
        service = AlgorithmService()
        with pytest.raises(ValueError, match="time_window_hours must be >= 0"):
            service._build_metrics_by_symptom(
                food_logs=[_food_log()],
                symptom_logs=[_symptom_log()],
                time_window_hours=-1.0,
            )

    def test_negative_time_window_silently_ignored_when_logs_are_empty(self):
        """
        BEHAVIOR NOTE: The empty-logs guard returns {} before reaching the
        ValueError check. A negative time_window with empty logs produces no
        error rather than raising ValueError. Callers relying on the error for
        validation may be surprised when logs happen to be empty.
        """
        service = AlgorithmService()
        # Should arguably raise, but currently returns {} silently.
        result = service._build_metrics_by_symptom(
            food_logs=[], symptom_logs=[], time_window_hours=-5.0
        )
        assert result == {}

    def test_food_id_becomes_ingredient_key(self):
        """Food IDs are encoded as pseudo-ingredient strings so the algorithm tracks food events."""
        food_id = uuid4()
        symptom_id = uuid4()
        result = AlgorithmService()._build_metrics_by_symptom(
            food_logs=[_food_log(food_id=food_id, timestamp="2024-01-01T08:00:00")],
            symptom_logs=[_symptom_log(symptom_id=symptom_id, timestamp="2024-01-01T10:00:00")],
            time_window_hours=4.0,
        )
        assert str(symptom_id) in result
        assert str(food_id) in result[str(symptom_id)]

    def test_symptom_id_becomes_outer_key(self):
        symptom_id = uuid4()
        result = AlgorithmService()._build_metrics_by_symptom(
            food_logs=[_food_log(timestamp="2024-01-01T08:00:00")],
            symptom_logs=[_symptom_log(symptom_id=symptom_id, timestamp="2024-01-01T10:00:00")],
            time_window_hours=4.0,
        )
        assert str(symptom_id) in result

    def test_food_outside_window_produces_no_association(self):
        """Food logged before the time window must not appear in results."""
        service = AlgorithmService()
        symptom_id = uuid4()
        result = service._build_metrics_by_symptom(
            food_logs=[_food_log(timestamp="2024-01-01T01:00:00")],
            # 2-hour window before 10:00 covers 08:00–10:00; food is at 01:00
            symptom_logs=[_symptom_log(symptom_id=symptom_id, timestamp="2024-01-01T10:00:00")],
            time_window_hours=2.0,
        )
        assert result == {}

    def test_metrics_shape_for_food_in_window(self):
        food_id = uuid4()
        symptom_id = uuid4()
        result = AlgorithmService()._build_metrics_by_symptom(
            food_logs=[_food_log(food_id=food_id, timestamp="2024-01-01T08:00:00")],
            symptom_logs=[_symptom_log(symptom_id=symptom_id, intensity=7, timestamp="2024-01-01T10:00:00")],
            time_window_hours=4.0,
        )
        m = result[str(symptom_id)][str(food_id)]
        assert m.exposures >= 1
        assert 0.0 <= m.trigger_rate <= 1.0
        assert 0.0 <= m.base_rate <= 1.0
        assert 0.0 <= m.fishers_p_value <= 1.0
        assert m.average_intensity == pytest.approx(7.0)

    def test_multiple_symptoms_produce_separate_keys(self):
        food_id = uuid4()
        symptom_a = uuid4()
        symptom_b = uuid4()
        result = AlgorithmService()._build_metrics_by_symptom(
            food_logs=[_food_log(food_id=food_id, timestamp="2024-01-01T08:00:00")],
            symptom_logs=[
                _symptom_log(symptom_id=symptom_a, timestamp="2024-01-01T10:00:00"),
                _symptom_log(symptom_id=symptom_b, timestamp="2024-01-01T11:00:00"),
            ],
            time_window_hours=4.0,
        )
        assert str(symptom_a) in result
        assert str(symptom_b) in result


# ---------------------------------------------------------------------------
# _serialize_metrics_rows
# ---------------------------------------------------------------------------


class TestSerializeMetricsRows:
    def test_empty_input_returns_empty_list(self):
        assert AlgorithmService()._serialize_metrics_rows([]) == []

    def test_valid_uuid_ingredient_is_serialized(self):
        food_id = uuid4()
        result = AlgorithmService()._serialize_metrics_rows([_metrics_row(ingredient=str(food_id))])
        assert len(result) == 1
        assert result[0].associated_food_id == food_id

    def test_non_uuid_ingredient_is_silently_skipped(self):
        """Rows with plain-text ingredients (e.g. from old runs) are dropped without error."""
        result = AlgorithmService()._serialize_metrics_rows([_metrics_row(ingredient="not-a-uuid")])
        assert result == []

    def test_mixed_rows_only_returns_valid_uuid_rows(self):
        good_id = uuid4()
        rows = [
            _metrics_row(ingredient=str(good_id)),
            _metrics_row(ingredient="plain-ingredient"),
        ]
        result = AlgorithmService()._serialize_metrics_rows(rows)
        assert len(result) == 1
        assert result[0].associated_food_id == good_id

    def test_all_fields_mapped_from_row(self):
        symptom_id = uuid4()
        food_id = uuid4()
        row = _metrics_row(
            username="alice",
            symptom_id=symptom_id,
            ingredient=str(food_id),
            exposures=3,
            trigger_rate=0.75,
            base_rate=0.25,
            fishers_p_value=0.01,
            average_intensity=6.5,
        )
        result = AlgorithmService()._serialize_metrics_rows([row])
        r = result[0]
        assert isinstance(r, AlgorithmAssociationResponse)
        assert r.user_id == "alice"
        assert r.symptom_id == symptom_id
        assert r.associated_food_id == food_id
        assert r.key_metrics.exposures == 3
        assert r.key_metrics.trigger_rate == pytest.approx(0.75)
        assert r.key_metrics.base_rate == pytest.approx(0.25)
        assert r.key_metrics.fishers_p_value == pytest.approx(0.01)
        assert r.key_metrics.average_intensity == pytest.approx(6.5)


# ---------------------------------------------------------------------------
# get_associations
# ---------------------------------------------------------------------------


class TestGetAssociations:
    def test_calls_get_by_symptom_for_each_symptom_id(self):
        symptom_a, symptom_b = uuid4(), uuid4()
        with patch("services.algorithm_service.MetricsRepository") as MockRepo:
            MockRepo.return_value.get_by_symptom.return_value = []
            AlgorithmService().get_associations(db=MagicMock(), user_id="alice", symptom_ids=[symptom_a, symptom_b])
            assert MockRepo.return_value.get_by_symptom.call_count == 2

    def test_calls_get_by_user_when_symptom_ids_is_none(self):
        with patch("services.algorithm_service.MetricsRepository") as MockRepo:
            MockRepo.return_value.get_by_user.return_value = []
            AlgorithmService().get_associations(db=MagicMock(), user_id="alice", symptom_ids=None)
            MockRepo.return_value.get_by_user.assert_called_once_with(username="alice")

    def test_empty_symptom_ids_list_falls_through_to_get_by_user(self):
        """
        BEHAVIOR NOTE: symptom_ids=[] is falsy, so the branch that calls get_by_symptom
        is skipped and get_by_user is called instead. This returns ALL metrics for the
        user. A caller passing [] may expect zero results or a scoped query, but gets
        everything. Consider treating [] as 'no filter' vs 'empty filter' explicitly.
        """
        with patch("services.algorithm_service.MetricsRepository") as MockRepo:
            MockRepo.return_value.get_by_user.return_value = []
            AlgorithmService().get_associations(db=MagicMock(), user_id="alice", symptom_ids=[])
            MockRepo.return_value.get_by_user.assert_called_once_with(username="alice")
            MockRepo.return_value.get_by_symptom.assert_not_called()

    def test_returns_list_of_algorithm_association_responses(self):
        symptom_id = uuid4()
        food_id = uuid4()
        row = _metrics_row(ingredient=str(food_id), symptom_id=symptom_id)
        with patch("services.algorithm_service.MetricsRepository") as MockRepo:
            MockRepo.return_value.get_by_symptom.return_value = [row]
            result = AlgorithmService().get_associations(
                db=MagicMock(), user_id="alice", symptom_ids=[symptom_id]
            )
        assert len(result) == 1
        assert isinstance(result[0], AlgorithmAssociationResponse)

    def test_non_uuid_ingredient_rows_excluded_from_response(self):
        symptom_id = uuid4()
        row = _metrics_row(ingredient="tomato", symptom_id=symptom_id)
        with patch("services.algorithm_service.MetricsRepository") as MockRepo:
            MockRepo.return_value.get_by_symptom.return_value = [row]
            result = AlgorithmService().get_associations(
                db=MagicMock(), user_id="alice", symptom_ids=[symptom_id]
            )
        assert result == []


# ---------------------------------------------------------------------------
# run_algorithm
# ---------------------------------------------------------------------------


class TestRunAlgorithm:
    def test_returns_empty_list_when_no_food_logs(self):
        payload = AlgorithmRunRequest(user_id="alice", symptom_ids=[uuid4()])
        service = AlgorithmService()
        with (
            patch.object(service, "_get_food_logs_for_user", return_value=[]),
            patch.object(service, "_get_symptom_logs_for_user", return_value=[_symptom_log()]),
            patch("services.algorithm_service.MetricsRepository") as MockRepo,
        ):
            MockRepo.return_value.get_by_symptom.return_value = []
            result = service.run_algorithm(db=MagicMock(), payload=payload)
        assert result == []

    def test_returns_empty_list_when_no_symptom_logs(self):
        payload = AlgorithmRunRequest(user_id="alice", symptom_ids=[uuid4()])
        service = AlgorithmService()
        with (
            patch.object(service, "_get_food_logs_for_user", return_value=[_food_log()]),
            patch.object(service, "_get_symptom_logs_for_user", return_value=[]),
            patch("services.algorithm_service.MetricsRepository") as MockRepo,
        ):
            MockRepo.return_value.get_by_symptom.return_value = []
            result = service.run_algorithm(db=MagicMock(), payload=payload)
        assert result == []

    def test_upsert_not_called_when_no_metrics_produced(self):
        payload = AlgorithmRunRequest(user_id="alice", symptom_ids=[uuid4()])
        service = AlgorithmService()
        with (
            patch.object(service, "_get_food_logs_for_user", return_value=[]),
            patch.object(service, "_get_symptom_logs_for_user", return_value=[]),
            patch("services.algorithm_service.MetricsRepository") as MockRepo,
        ):
            MockRepo.return_value.get_by_user.return_value = []
            service.run_algorithm(db=MagicMock(), payload=payload)
            MockRepo.return_value.upsert_metrics.assert_not_called()

    def test_upsert_called_once_per_symptom_with_associations(self):
        symptom_a, symptom_b = uuid4(), uuid4()
        food_id = uuid4()
        payload = AlgorithmRunRequest(user_id="alice", symptom_ids=[symptom_a, symptom_b])
        service = AlgorithmService()
        with (
            patch.object(
                service,
                "_get_food_logs_for_user",
                return_value=[_food_log(food_id=food_id, timestamp="2024-01-01T08:00:00")],
            ),
            patch.object(
                service,
                "_get_symptom_logs_for_user",
                return_value=[
                    _symptom_log(symptom_id=symptom_a, timestamp="2024-01-01T10:00:00"),
                    _symptom_log(symptom_id=symptom_b, timestamp="2024-01-01T11:00:00"),
                ],
            ),
            patch("services.algorithm_service.MetricsRepository") as MockRepo,
        ):
            MockRepo.return_value.get_by_symptom.return_value = []
            service.run_algorithm(db=MagicMock(), payload=payload)
        # One upsert per symptom key that the algorithm produced
        assert MockRepo.return_value.upsert_metrics.call_count == 2

    def test_get_associations_called_with_payload_symptom_ids(self):
        """run_algorithm must forward the original symptom_ids to get_associations."""
        symptom_id = uuid4()
        payload = AlgorithmRunRequest(user_id="alice", symptom_ids=[symptom_id])
        service = AlgorithmService()
        with (
            patch.object(service, "_get_food_logs_for_user", return_value=[]),
            patch.object(service, "_get_symptom_logs_for_user", return_value=[]),
            patch.object(service, "get_associations", return_value=[]) as mock_get,
            patch("services.algorithm_service.MetricsRepository"),
        ):
            service.run_algorithm(db=MagicMock(), payload=payload)
        assert mock_get.call_args.kwargs["user_id"] == "alice"
        assert mock_get.call_args.kwargs["symptom_ids"] == [symptom_id]

    def test_empty_symptom_ids_fetches_all_symptom_logs(self):
        """
        BEHAVIOR NOTE: AlgorithmRunRequest defaults symptom_ids to []. An empty list
        is falsy, so _get_symptom_logs_for_user applies no WHERE-IN filter and returns
        every symptom log for the user. Callers may not expect an empty list to mean
        'all symptoms'. This also means the subsequent get_associations call hits
        get_by_user, returning all stored metrics rather than a scoped subset.
        """
        payload = AlgorithmRunRequest(user_id="alice")  # symptom_ids=[] by default
        service = AlgorithmService()
        with (
            patch.object(service, "_get_food_logs_for_user", return_value=[]),
            patch.object(service, "_get_symptom_logs_for_user", return_value=[]) as mock_symp,
            patch.object(service, "get_associations", return_value=[]),
            patch("services.algorithm_service.MetricsRepository"),
        ):
            service.run_algorithm(db=MagicMock(), payload=payload)
        # Symptom log query was called with an empty list — no symptom filter applied
        assert mock_symp.call_args.args[2] == []


# ---------------------------------------------------------------------------
# _build_association_rows  (helper, not on the main run_algorithm path)
# ---------------------------------------------------------------------------


class TestBuildAssociationRows:
    def test_basic_shape(self):
        """Existing coverage: verify row dict contains expected keys and metric fields."""
        service = AlgorithmService()
        food_a, food_b, symptom_headache = uuid4(), uuid4(), uuid4()
        rows = service._build_association_rows(
            user_id="alice",
            food_logs=[
                _food_log(food_id=food_a, timestamp="2024-01-01T08:00:00"),
                _food_log(food_id=food_b, timestamp="2024-01-01T09:00:00"),
                _food_log(food_id=food_a, timestamp="2024-01-01T12:00:00"),
            ],
            symptom_logs=[
                _symptom_log(symptom_id=symptom_headache, intensity=6, timestamp="2024-01-01T10:00:00"),
            ],
            time_window_hours=3,
        )
        assert rows
        for row in rows:
            assert row["user_id"] == "alice"
            assert row["symptom_id"] == symptom_headache
            assert "associated_food_id" in row
            m = IngredientSymptomMetrics(**row["key_metrics"])
            assert m.exposures >= 0
            assert m.trigger_rate >= 0
            assert m.base_rate >= 0
            assert m.fishers_p_value >= 0
            assert m.average_intensity >= 0

    def test_returns_empty_list_when_no_logs(self):
        rows = AlgorithmService()._build_association_rows(
            user_id="alice", food_logs=[], symptom_logs=[], time_window_hours=4.0
        )
        assert rows == []

    def test_not_used_by_run_algorithm_dead_code(self):
        """
        BEHAVIOR NOTE: _build_association_rows is not called by run_algorithm.
        run_algorithm calls _build_metrics_by_symptom directly and delegates
        persistence to MetricsRepository. This method appears to be dead code
        left over from an earlier design and could be removed to avoid confusion.
        """
        import inspect

        source = inspect.getsource(AlgorithmService.run_algorithm)
        assert "_build_association_rows" not in source


# ---------------------------------------------------------------------------
# _get_food_logs_for_user / _get_symptom_logs_for_user
# ---------------------------------------------------------------------------


class TestGetLogsForUser:
    def _mock_db(self, rows):
        """Return a db mock whose execute().scalars().all() yields rows."""
        db = MagicMock()
        db.execute.return_value.scalars.return_value.all.return_value = rows
        return db

    def test_get_food_logs_returns_db_results(self):
        expected = [_food_log(), _food_log()]
        db = self._mock_db(expected)
        result = AlgorithmService()._get_food_logs_for_user(db, "alice")
        assert result == expected
        db.execute.assert_called_once()

    def test_get_food_logs_returns_empty_list(self):
        db = self._mock_db([])
        result = AlgorithmService()._get_food_logs_for_user(db, "alice")
        assert result == []

    def test_get_symptom_logs_without_filter_returns_db_results(self):
        expected = [_symptom_log(), _symptom_log()]
        db = self._mock_db(expected)
        result = AlgorithmService()._get_symptom_logs_for_user(db, "alice", symptom_ids=None)
        assert result == expected
        db.execute.assert_called_once()

    def test_get_symptom_logs_with_symptom_ids_filter(self):
        """Passing symptom_ids appends a WHERE IN clause to the query."""
        symptom_id = uuid4()
        expected = [_symptom_log(symptom_id=symptom_id)]
        db = self._mock_db(expected)
        result = AlgorithmService()._get_symptom_logs_for_user(db, "alice", symptom_ids=[symptom_id])
        assert result == expected
        db.execute.assert_called_once()

    def test_get_symptom_logs_with_empty_symptom_ids_skips_filter(self):
        """
        BEHAVIOR NOTE (mirrors get_associations): symptom_ids=[] is falsy so the
        WHERE IN branch is skipped. All symptom logs for the user are returned,
        not zero rows as one might expect from passing an empty list.
        """
        expected = [_symptom_log(), _symptom_log()]
        db = self._mock_db(expected)
        result = AlgorithmService()._get_symptom_logs_for_user(db, "alice", symptom_ids=[])
        # Returns everything — no IN filter applied
        assert result == expected
