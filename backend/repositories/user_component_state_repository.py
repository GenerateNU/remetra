from sqlalchemy import select
from sqlalchemy.orm import Session

from models.component import Component
from models.user import User
from models.user_component_state import UserComponentState


class UserComponentStateRepository:

    def has_state(self, db: Session, username: str) -> bool:
        result = db.execute(
            select(UserComponentState.id).where(UserComponentState.username == username).limit(1)
        ).scalar_one_or_none()
        return result is not None

    def bulk_insert(self, db: Session, rows: list[UserComponentState]) -> None:
        db.add_all(rows)
        db.commit()

    def get_all_components(self, db: Session) -> list[Component]:
        return db.query(Component).all()

    def get_user(self, db: Session, username: str) -> User:
        return db.query(User).filter(User.username == username).one()

    def get_states_for_user(self, db: Session, username: str) -> list[UserComponentState]:
        return db.query(UserComponentState).filter(UserComponentState.username == username).all()

    def update_states(self, db: Session, states: list[UserComponentState]) -> None:
        db.add_all(states)
        db.commit()
