from sqlalchemy.orm import Session

from repositories.daily_check_in_repository import DailyCheckInRepository
from schemas.daily_check_in import DailyCheckInCreate, DailyCheckInResponse


class DailyCheckInService:
    """Business logic for daily check-ins."""

    def __init__(self):
        self.repo = DailyCheckInRepository()

    def check_in_no_symptoms(self, db: Session, username: str, data: DailyCheckInCreate) -> DailyCheckInResponse:
        """Record a no-symptoms check-in. Repeating it for the same date returns the existing row."""
        existing = self.repo.get_by_date(db, username, data.date)
        if existing:
            return DailyCheckInResponse.model_validate(existing)
        check_in = self.repo.create(db, username, data)
        return DailyCheckInResponse.model_validate(check_in)
