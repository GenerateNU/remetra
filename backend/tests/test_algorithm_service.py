"""Unit tests for AlgorithmService."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from models.food import Food
from models.food_log import FoodLog
from models.metrics import Metrics
from models.symptom_log import SymptomLog
from schemas.algorithm import AlgorithmAssociationResponse, AlgorithmRunRequest
from services.algorithm_service import AlgorithmService


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _food_log(username="alice", food_id=None, timestamp="2024-01-01T08:00:00", ingredients=None) -> FoodLog:
    log = FoodLog()
    log.id = uuid4()
    log.username = username
    log.food_id = food_id or uuid4()
    log.timestamp = _dt(timestamp)
    # Attach a Food object with ingredients for per-ingredient analysis
    food = Food()
    food.id = log.food_id
    food.name = "test_food"
    food.ingredients = ingredients or []
    log.food = food
    return log


def _symptom_log(username="alice", symptom_id=None, intensity=5, timestamp="2024-01-01T10:00:00") -> SymptomLog:
    log = SymptomLog()
    log.id = uuid4()
    log.username = username
    log.symptom_id = symptom_id or uuid4()
    log.intensity = intensity
    log.timestamp = _dt(timestamp)
    return log


def _metrics_row(username="alice", symptom_id=None, ingredient="gluten", **overrides) -> Metrics:
    row = Metrics()
    row.id = uuid4()
    row.username = username
    row.symptom_id = symptom_id or uuid4()
    row.ingredient = ingredient
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
        result = service._build_metrics_by_symptom(food_logs=[], symptom_logs=[_symptom_log()], time_window_hours=4.0)
        assert result == {}

    def test_returns_empty_dict_when_no_symptom_logs(self):
        service = AlgorithmService()
        result = service._build_metrics_by_symptom(
            food_logs=[_food_log(ingredients=["gluten"])], symptom_logs=[], time_window_hours=4.0
        )
        assert result == {}

    def test_returns_empty_dict_when_both_empty(self):
        service = AlgorithmService()
        assert service._build_metrics_by_symptom(food_logs=[], symptom_logs=[], time_window_hours=4.0) == {}

    def test_raises_for_negative_time_window(self):
        service = AlgorithmService()
        with pytest.raises(ValueError, match="time_window_hours must be >= 0"):
            service._build_metrics_by_symptom(
                food_logs=[_food_log(ingredients=["gluten"])],
                symptom_logs=[_symptom_log()],
                time_window_hours=-1.0,
            )

    def test_negative_time_window_silently_ignored_when_logs_are_empty(self):
        service = AlgorithmService()
        result = service._build_metrics_by_symptom(food_logs=[], symptom_logs=[], time_window_hours=-5.0)
        assert result == {}

    def test_ingredient_name_becomes_inner_key(self):
        """Actual ingredient names (not food UUIDs) are used as keys in the result."""
        symptom_id = uuid4()
        result = AlgorithmService()._build_metrics_by_symptom(
            food_logs=[_food_log(timestamp="2024-01-01T08:00:00", ingredients=["gluten", "dairy"])],
            symptom_logs=[_symptom_log(symptom_id=symptom_id, timestamp="2024-01-01T10:00:00")],
            time_window_hours=4.0,
        )
        assert str(symptom_id) in result
        assert "gluten" in result[str(symptom_id)]
        assert "dairy" in result[str(symptom_id)]

    def test_symptom_id_becomes_outer_key(self):
        symptom_id = uuid4()
        result = AlgorithmService()._build_metrics_by_symptom(
            food_logs=[_food_log(timestamp="2024-01-01T08:00:00", ingredients=["gluten"])],
            symptom_logs=[_symptom_log(symptom_id=symptom_id, timestamp="2024-01-01T10:00:00")],
            time_window_hours=4.0,
        )
        assert str(symptom_id) in result

    def test_food_outside_window_produces_no_association(self):
        service = AlgorithmService()
        symptom_id = uuid4()
        result = service._build_metrics_by_symptom(
            food_logs=[_food_log(timestamp="2024-01-01T01:00:00", ingredients=["gluten"])],
            symptom_logs=[_symptom_log(symptom_id=symptom_id, timestamp="2024-01-01T10:00:00")],
            time_window_hours=2.0,
        )
        assert result == {}

    def test_metrics_shape_for_ingredient_in_window(self):
        symptom_id = uuid4()
        result = AlgorithmService()._build_metrics_by_symptom(
            food_logs=[_food_log(timestamp="2024-01-01T08:00:00", ingredients=["gluten"])],
            symptom_logs=[_symptom_log(symptom_id=symptom_id, intensity=7, timestamp="2024-01-01T10:00:00")],
            time_window_hours=4.0,
        )
        m = result[str(symptom_id)]["gluten"]
        assert m.exposures >= 1
        assert 0.0 <= m.trigger_rate <= 1.0
        assert 0.0 <= m.base_rate <= 1.0
        assert 0.0 <= m.fishers_p_value <= 1.0
        assert m.average_intensity == pytest.approx(7.0)

    def test_multiple_symptoms_produce_separate_keys(self):
        symptom_a = uuid4()
        symptom_b = uuid4()
        result = AlgorithmService()._build_metrics_by_symptom(
            food_logs=[_food_log(timestamp="2024-01-01T08:00:00", ingredients=["gluten"])],
            symptom_logs=[
                _symptom_log(symptom_id=symptom_a, timestamp="2024-01-01T10:00:00"),
                _symptom_log(symptom_id=symptom_b, timestamp="2024-01-01T11:00:00"),
            ],
            time_window_hours=4.0,
        )
        assert str(symptom_a) in result
        assert str(symptom_b) in result

    def test_food_with_no_ingredients_is_skipped(self):
        """Food logs with empty ingredients produce no associations."""
        symptom_id = uuid4()
        result = AlgorithmService()._build_metrics_by_symptom(
            food_logs=[_food_log(timestamp="2024-01-01T08:00:00", ingredients=[])],
            symptom_logs=[_symptom_log(symptom_id=symptom_id, timestamp="2024-01-01T10:00:00")],
            time_window_hours=4.0,
        )
        assert result == {}

    def test_shared_ingredient_across_foods(self):
        """Two foods both containing 'salt' should aggregate correctly."""
        symptom_id = uuid4()
        result = AlgorithmService()._build_metrics_by_symptom(
            food_logs=[
                _food_log(timestamp="2024-01-01T08:00:00", ingredients=["gluten", "salt"]),
                _food_log(timestamp="2024-01-01T09:00:00", ingredients=["dairy", "salt"]),
            ],
            symptom_logs=[_symptom_log(symptom_id=symptom_id, timestamp="2024-01-01T11:00:00")],
            time_window_hours=4.0,
        )
        symptom_metrics = result[str(symptom_id)]
        assert "gluten" in symptom_metrics
        assert "dairy" in symptom_metrics
        assert "salt" in symptom_metrics
        # salt appeared in 2 food events
        assert symptom_metrics["salt"].exposures == 2


# ---------------------------------------------------------------------------
# _serialize_metrics_rows
# ---------------------------------------------------------------------------


class TestSerializeMetricsRows:
    def test_empty_input_returns_empty_list(self):
        assert AlgorithmService()._serialize_metrics_rows([]) == []

    def test_ingredient_name_is_preserved(self):
        result = AlgorithmService()._serialize_metrics_rows([_metrics_row(ingredient="gluten")])
        assert len(result) == 1
        assert result[0].ingredient_name == "gluten"

    def test_all_fields_mapped_from_row(self):
        symptom_id = uuid4()
        row = _metrics_row(
            username="alice",
            symptom_id=symptom_id,
            ingredient="dairy",
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
        assert r.ingredient_name == "dairy"
        assert r.key_metrics.exposures == 3
        assert r.key_metrics.trigger_rate == pytest.approx(0.75)
        assert r.key_metrics.base_rate == pytest.approx(0.25)
        assert r.key_metrics.fishers_p_value == pytest.approx(0.01)
        assert r.key_metrics.average_intensity == pytest.approx(6.5)

    def test_multiple_rows_all_serialized(self):
        rows = [
            _metrics_row(ingredient="gluten"),
            _metrics_row(ingredient="dairy"),
            _metrics_row(ingredient="tomato"),
        ]
        result = AlgorithmService()._serialize_metrics_rows(rows)
        assert len(result) == 3
        names = {r.ingredient_name for r in result}
        assert names == {"gluten", "dairy", "tomato"}


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
        with patch("services.algorithm_service.MetricsRepository") as MockRepo:
            MockRepo.return_value.get_by_user.return_value = []
            AlgorithmService().get_associations(db=MagicMock(), user_id="alice", symptom_ids=[])
            MockRepo.return_value.get_by_user.assert_called_once_with(username="alice")
            MockRepo.return_value.get_by_symptom.assert_not_called()

    def test_returns_list_of_algorithm_association_responses(self):
        symptom_id = uuid4()
        row = _metrics_row(ingredient="gluten", symptom_id=symptom_id)
        with patch("services.algorithm_service.MetricsRepository") as MockRepo:
            MockRepo.return_value.get_by_symptom.return_value = [row]
            result = AlgorithmService().get_associations(db=MagicMock(), user_id="alice", symptom_ids=[symptom_id])
        assert len(result) == 1
        assert isinstance(result[0], AlgorithmAssociationResponse)
        assert result[0].ingredient_name == "gluten"


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
            patch.object(service, "_get_food_logs_for_user", return_value=[_food_log(ingredients=["gluten"])]),
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
        payload = AlgorithmRunRequest(user_id="alice", symptom_ids=[symptom_a, symptom_b])
        service = AlgorithmService()
        with (
            patch.object(
                service,
                "_get_food_logs_for_user",
                return_value=[_food_log(timestamp="2024-01-01T08:00:00", ingredients=["gluten"])],
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
        assert MockRepo.return_value.upsert_metrics.call_count == 2

    def test_get_associations_called_with_payload_symptom_ids(self):
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
        payload = AlgorithmRunRequest(user_id="alice")
        service = AlgorithmService()
        with (
            patch.object(service, "_get_food_logs_for_user", return_value=[]),
            patch.object(service, "_get_symptom_logs_for_user", return_value=[]) as mock_symp,
            patch.object(service, "get_associations", return_value=[]),
            patch("services.algorithm_service.MetricsRepository"),
        ):
            service.run_algorithm(db=MagicMock(), payload=payload)
        assert mock_symp.call_args.args[2] == []


# ---------------------------------------------------------------------------
# _get_food_logs_for_user / _get_symptom_logs_for_user
# ---------------------------------------------------------------------------


class TestGetLogsForUser:
    def _mock_db(self, rows):
        """Return a db mock whose execute().unique().scalars().all() yields rows."""
        db = MagicMock()
        db.execute.return_value.unique.return_value.scalars.return_value.all.return_value = rows
        # Also support non-unique path for symptom logs
        db.execute.return_value.scalars.return_value.all.return_value = rows
        return db

    def test_get_food_logs_returns_db_results(self):
        expected = [_food_log(ingredients=["gluten"]), _food_log(ingredients=["dairy"])]
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
        symptom_id = uuid4()
        expected = [_symptom_log(symptom_id=symptom_id)]
        db = self._mock_db(expected)
        result = AlgorithmService()._get_symptom_logs_for_user(db, "alice", symptom_ids=[symptom_id])
        assert result == expected
        db.execute.assert_called_once()

    def test_get_symptom_logs_with_empty_symptom_ids_skips_filter(self):
        expected = [_symptom_log(), _symptom_log()]
        db = self._mock_db(expected)
        result = AlgorithmService()._get_symptom_logs_for_user(db, "alice", symptom_ids=[])
        assert result == expected
