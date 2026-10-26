from collections import Counter
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from analysis.models import FoodLogEntry
from analysis.pool_picker import (
    build_user_context,
    components_in_log,
    eligible_ingredients,
    rank_pool,
)
from auth_context import current_username
from repositories.food_log_repository import FoodLogRepository
from repositories.ingredient_pool_repository import IngredientPoolRepository
from repositories.user_repository import UserRepository
from schemas.ingredient_pool import IngredientPoolResponse
from services.symptom_log_service import SymptomLogService
from services.taxonomy_service import TaxonomyService


class IngredientPoolService:
    def __init__(self):
        self.ingredient_pool_repo = IngredientPoolRepository()
        self.user_repo = UserRepository()
        self.food_log_repo = FoodLogRepository()
        self.symptom_log_service = SymptomLogService()
        self.taxonomy = TaxonomyService()

    def get_today_pool(self, db: Session) -> IngredientPoolResponse:
        username = current_username.get()
        if not username:
            raise ValueError("Authenticated user is required")

        now = datetime.now(timezone.utc)
        today = now.date()

        existing = self.ingredient_pool_repo.get_by_user_and_date(db, username, today)
        if existing:
            return IngredientPoolResponse.model_validate(existing)

        user = self.user_repo.get_by_username(db, username)
        if user is None:
            raise ValueError(f"User {username!r} not found")

        logs = self.food_log_repo.get_food_logs_by_username(db, username)
        start = now - timedelta(days=30)

        food_logs: list[FoodLogEntry] = []
        for log in logs:
            timestamp = log.timestamp
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            else:
                timestamp = timestamp.astimezone(timezone.utc)

            if not start <= timestamp <= now or log.food is None:
                continue

            food_logs.append(
                FoodLogEntry(
                    timestamp=timestamp,
                    ingredients=log.food.ingredients or [],
                )
            )

        washout = self.symptom_log_service.get_washout_status(db, now)

        context = build_user_context(
            user.disease,
            food_logs,
            self.taxonomy.lookup,
            now,
        )
        eligible = eligible_ingredients(
            self.taxonomy.data,
            context,
            washout,
        )

        recent_counts = self._count_recent_components(food_logs, now)
        ingredient_ids = rank_pool(
            eligible,
            self.taxonomy.data,
            recent_counts,
        )

        saved = self.ingredient_pool_repo.create(
            db,
            username,
            today,
            ingredient_ids,
            washout.active,
        )
        return IngredientPoolResponse.model_validate(saved)

    def _count_recent_components(
        self,
        food_logs: list[FoodLogEntry],
        now: datetime,
    ) -> dict[str, int]:
        start = now - timedelta(days=14)
        counts: Counter[str] = Counter()

        for log in food_logs:
            timestamp = log.timestamp
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            else:
                timestamp = timestamp.astimezone(timezone.utc)

            if start <= timestamp <= now:
                # Count each component at most once per food-log event.
                counts.update(components_in_log(log.ingredients, self.taxonomy.lookup))

        return dict(counts)
