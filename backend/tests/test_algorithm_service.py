"""Unit tests for AlgorithmService association logic."""

from datetime import datetime
from uuid import uuid4

from analysis.models import IngredientSymptomMetrics
from models.food_log import FoodLog
from models.symptom_log import SymptomLog
from services.algorithm_service import AlgorithmService


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def test_build_association_rows_with_expected_key_metrics_shape():
    service = AlgorithmService()

    food_a = uuid4()
    food_b = uuid4()
    symptom_headache = uuid4()

    food_logs = [
        FoodLog(id=uuid4(), username="alice", food_id=food_a, timestamp=_dt("2024-01-01T08:00:00")),
        FoodLog(id=uuid4(), username="alice", food_id=food_b, timestamp=_dt("2024-01-01T09:00:00")),
        FoodLog(id=uuid4(), username="alice", food_id=food_a, timestamp=_dt("2024-01-01T12:00:00")),
    ]
    symptom_logs = [
        SymptomLog(
            id=uuid4(),
            username="alice",
            symptom_id=symptom_headache,
            intensity=6,
            timestamp=_dt("2024-01-01T10:00:00"),
        )
    ]

    rows = service._build_association_rows(
        user_id="alice",
        food_logs=food_logs,
        symptom_logs=symptom_logs,
        time_window_hours=3,
    )

    assert rows
    for row in rows:
        assert row["user_id"] == "alice"
        assert row["symptom_id"] == symptom_headache
        assert "associated_food_id" in row

        metrics = IngredientSymptomMetrics(**row["key_metrics"])
        assert metrics.exposures >= 0
        assert metrics.trigger_rate >= 0
        assert metrics.base_rate >= 0
        assert metrics.fishers_p_value >= 0
        assert metrics.average_intensity >= 0
