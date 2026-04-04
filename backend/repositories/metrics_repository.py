"""Repository for ingredient symptom metrics."""

from uuid import UUID

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from models.metrics import Metrics


class MetricsRepository:
    """Handles all DB operations for ingredient_symptom_metrics."""

    def __init__(self, db: Session):
        self.db = db

    def upsert_metrics(
        self,
        username: str,
        symptom_id: UUID,
        metrics_by_ingredient: dict,
    ) -> None:
        """
        Bulk upsert metrics for a single (username, symptom_id) pair.

        Args:
            username: The user these metrics belong to.
            symptom_id: The symptom UUID being analyzed.
            metrics_by_ingredient: Dict of ingredient -> IngredientSymptomMetrics
                                   (the inner dict from get_analysis() output).
        """
        if not metrics_by_ingredient:
            return

        rows = [
            {
                "username": username,
                "symptom_id": symptom_id,
                "ingredient": ingredient,
                "exposures": m.exposures,
                "trigger_rate": m.trigger_rate,
                "base_rate": m.base_rate,
                "fishers_p_value": m.fishers_p_value,
                "average_intensity": m.average_intensity,
            }
            for ingredient, m in metrics_by_ingredient.items()
        ]

        stmt = insert(Metrics).values(rows)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_user_symptom_ingredient",
            set_={
                "exposures": stmt.excluded.exposures,
                "trigger_rate": stmt.excluded.trigger_rate,
                "base_rate": stmt.excluded.base_rate,
                "fishers_p_value": stmt.excluded.fishers_p_value,
                "average_intensity": stmt.excluded.average_intensity,
                "updated_at": stmt.excluded.updated_at,
            },
        )

        self.db.execute(stmt)
        self.db.commit()

    def get_by_symptom(
        self,
        username: str,
        symptom_id: UUID,
    ) -> list[Metrics]:
        """
        Fetch all ingredient metrics for a user + symptom, sorted by exposures desc.
        """
        return (
            self.db.query(Metrics)
            .filter_by(username=username, symptom_id=symptom_id)
            .order_by(Metrics.exposures.desc())
            .all()
        )

    def get_by_user(
        self,
        username: str,
    ) -> list[Metrics]:
        """
        Fetch all ingredient metrics for a user across all symptoms, sorted by exposures desc.
        """
        return self.db.query(Metrics).filter_by(username=username).order_by(Metrics.exposures.desc()).all()
