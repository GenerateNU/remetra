"""Service layer for meal follow up business logic."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from repositories.food_log_repository import FoodLogRepository

FOLLOW_UP_DELAY = timedelta(hours=2)


class MealFollowUpsService:
    """Service for meal follow ups business logic."""

    def __init__(self):
        self.food_log_repo = FoodLogRepository()

    def should_schedule(self, db: Session, food_log_id: UUID, now: Optional[datetime] = None) -> Optional[bool]:
        """Return True if the food log is within the 2 hour follow up window, None if the log doesn't exist."""
        food_log = self.food_log_repo.get_food_log_by_id(db, food_log_id)
        if not food_log:
            return None
        now = now or datetime.now(timezone.utc)
        return now - food_log.timestamp < FOLLOW_UP_DELAY

    def when_to_fire(self, db: Session, food_log_id: UUID) -> Optional[datetime]:
        """Calculate when the notification should be fired, None if the log doesn't exist."""
        food_log = self.food_log_repo.get_food_log_by_id(db, food_log_id)
        if not food_log:
            return None
        return food_log.timestamp + FOLLOW_UP_DELAY

    def build_message(self, db: Session, food_log_id: UUID) -> Optional[str]:
        """Build the notification message, None if the log doesn't exist."""
        food_log = self.food_log_repo.get_food_log_by_id(db, food_log_id)
        if not food_log:
            return None
        return f"It's been a couple hours since your {food_log.food.name}. Any symptoms to log?"
