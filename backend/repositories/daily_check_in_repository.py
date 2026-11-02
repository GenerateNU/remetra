from datetime import date

import sqlalchemy as sa
from sqlalchemy.orm import Session

from models.daily_check_in import DailyCheckIn
from schemas.daily_check_in import DailyCheckInCreate


class DailyCheckInRepository:
    def get_by_date(self, db: Session, username: str, check_in_date: date):
        query = sa.select(DailyCheckIn).where(
            DailyCheckIn.username == username,
            DailyCheckIn.date == check_in_date,
        )
        result = db.execute(query)
        return result.scalar_one_or_none()

    def create(self, db: Session, username: str, data: DailyCheckInCreate):
        check_in = DailyCheckIn(username=username, **data.model_dump())
        db.add(check_in)
        db.commit()
        db.refresh(check_in)
        return check_in

    def get_check_in_dates(self, db: Session, username: str, start: date, end: date) -> set[date]:
        query = sa.select(DailyCheckIn.date).where(
            DailyCheckIn.username == username,
            DailyCheckIn.date >= start,
            DailyCheckIn.date <= end,
        )
        result = db.execute(query)
        return set(result.scalars().all())