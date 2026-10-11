from sqlalchemy.orm import Session

from repositories.health_repository import HealthRepository
from schemas.health import HealthSyncRequest, HealthSyncResponse


class HealthSyncService:
    """Business logic for health sync."""

    def __init__(self):
        self.repo = HealthRepository()

    def sync(self, db: Session, username: str, request: HealthSyncRequest) -> HealthSyncResponse:
        days_saved = self.repo.save_days(db, username, request.timezone, request.days)
        events_added = self.repo.save_events(db, username, request.events)
        events_skipped = len(request.events) - events_added
        return HealthSyncResponse(
            days_saved=days_saved,
            events_added=events_added, 
            events_skipped=events_skipped,
            )