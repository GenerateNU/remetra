"""Service layer for symptom-food association algorithm."""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from analysis.algorithm import get_analysis
from analysis.models import FoodLogEntry, SymptomLogEntry
from models.food_log import FoodLog
from models.metrics import Metrics
from models.symptom_log import SymptomLog
from repositories.metrics_repository import MetricsRepository
from schemas.algorithm import AlgorithmAssociationResponse, AlgorithmRunRequest


class AlgorithmService:
    """Runs symptom-food association analysis and persists results."""

    def __init__(self):
        self.repo: MetricsRepository | None = None

    def run_algorithm(self, db: Session, payload: AlgorithmRunRequest) -> list[AlgorithmAssociationResponse]:
        self.repo = MetricsRepository(db)
        food_logs = self._get_food_logs_for_user(db, payload.user_id)
        symptom_logs = self._get_symptom_logs_for_user(db, payload.user_id, payload.symptom_ids)

        metrics_by_symptom = self._build_metrics_by_symptom(
            food_logs=food_logs,
            symptom_logs=symptom_logs,
            time_window_hours=payload.time_window_hours,
        )

        for symptom_id_str, metrics_by_food_id in metrics_by_symptom.items():
            self.repo.upsert_metrics(
                username=payload.user_id,
                symptom_id=UUID(symptom_id_str),
                metrics_by_ingredient=metrics_by_food_id,
            )

        return self.get_associations(db=db, user_id=payload.user_id, symptom_ids=payload.symptom_ids)

    def get_associations(
        self,
        db: Session,
        user_id: str,
        symptom_ids: Sequence[UUID] | None = None,
    ) -> list[AlgorithmAssociationResponse]:
        self.repo = MetricsRepository(db)
        metrics_rows: list[Metrics] = []
        if symptom_ids:
            for symptom_id in symptom_ids:
                metrics_rows.extend(self.repo.get_by_symptom(username=user_id, symptom_id=symptom_id))
        else:
            metrics_rows = self.repo.get_by_user(username=user_id)

        return self._serialize_metrics_rows(metrics_rows)

    def _get_food_logs_for_user(self, db: Session, user_id: str) -> list[FoodLog]:
        query = select(FoodLog).where(FoodLog.username == user_id).order_by(FoodLog.timestamp.asc())
        result = db.execute(query)
        return result.scalars().all()

    def _get_symptom_logs_for_user(
        self,
        db: Session,
        user_id: str,
        symptom_ids: Sequence[UUID] | None,
    ) -> list[SymptomLog]:
        query = select(SymptomLog).where(SymptomLog.username == user_id).order_by(SymptomLog.timestamp.asc())
        if symptom_ids:
            query = query.where(SymptomLog.symptom_id.in_(symptom_ids))

        result = db.execute(query)
        return result.scalars().all()

    def _build_metrics_by_symptom(
        self,
        food_logs: list[FoodLog],
        symptom_logs: list[SymptomLog],
        time_window_hours: float,
    ) -> dict:
        if not food_logs or not symptom_logs:
            return {}

        if time_window_hours < 0:
            raise ValueError("time_window_hours must be >= 0")

        # Feed algorithm.py with food IDs encoded as pseudo-ingredients and symptom IDs as names.
        analysis_food_logs = [
            FoodLogEntry(timestamp=log.timestamp, ingredients=[str(log.food_id)])
            for log in food_logs
        ]
        analysis_symptom_logs = [
            SymptomLogEntry(timestamp=log.timestamp, symptom_name=str(log.symptom_id), intensity=log.intensity)
            for log in symptom_logs
        ]
        return get_analysis(
            food_logs=analysis_food_logs,
            symptom_logs=analysis_symptom_logs,
            time_window_hours=time_window_hours,
        )

    def _serialize_metrics_rows(
        self,
        metrics_rows: list[Metrics],
    ) -> list[AlgorithmAssociationResponse]:
        response_rows: list[AlgorithmAssociationResponse] = []
        for row in metrics_rows:
            try:
                associated_food_id = UUID(row.ingredient)
            except ValueError:
                # Ignore non-UUID ingredient rows that may exist from older runs.
                continue

            response_rows.append(
                AlgorithmAssociationResponse.model_validate(
                    {
                        "id": row.id,
                        "user_id": row.username,
                        "symptom_id": row.symptom_id,
                        "associated_food_id": associated_food_id,
                        "key_metrics": {
                            "exposures": row.exposures,
                            "trigger_rate": row.trigger_rate,
                            "base_rate": row.base_rate,
                            "fishers_p_value": row.fishers_p_value,
                            "average_intensity": row.average_intensity,
                        },
                        "updated_at": row.updated_at,
                    }
                )
            )

        return response_rows
