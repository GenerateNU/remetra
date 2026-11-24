from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.user_model_run import UserModelRun


class UserModelRunRepository:
    """Access to when the nightly model last ran for each user."""

    def get(self, db: Session, username: str) -> UserModelRun | None:
        return db.execute(select(UserModelRun).where(UserModelRun.username == username)).scalar_one_or_none()

    def create(self, db: Session, username: str, last_update: datetime) -> UserModelRun:
        try:
            run = UserModelRun(username=username, last_update=last_update)
            db.add(run)
            db.commit()
            return run
        except Exception:
            db.rollback()
            raise

    def set_last_update(self, db: Session, run: UserModelRun, last_update: datetime) -> None:
        try:
            run.last_update = last_update
            db.commit()
        except Exception:
            db.rollback()
            raise
