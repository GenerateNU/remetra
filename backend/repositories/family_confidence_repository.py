from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, contains_eager

from analysis.model_constants import INITIAL_LOG_ODDS
from models.component import Component
from models.symptom_family import MODELED_FAMILIES, SymptomFamily
from models.user_background_total import UserBackgroundTotal
from models.user_family_confidence import UserFamilyConfidence


class FamilyConfidenceRepository:
    """Access to a user's per-family component confidences and background totals."""

    def initialize_for_user(self, db: Session, username: str) -> None:
        """Insert a confidence row for every component and family, and a background total for every family.

        Idempotent: rows that already exist are left alone, so calling this twice changes nothing.
        """
        try:
            component_ids = db.execute(sa.select(Component.id)).scalars().all()
            confidence_rows = [
                {
                    "username": username,
                    "component_id": component_id,
                    "family": family.value,
                    "log_odds": INITIAL_LOG_ODDS,
                }
                for component_id in component_ids
                for family in MODELED_FAMILIES
            ]
            if confidence_rows:
                db.execute(insert(UserFamilyConfidence).values(confidence_rows).on_conflict_do_nothing())
            background_rows = [{"username": username, "family": family.value} for family in MODELED_FAMILIES]
            db.execute(insert(UserBackgroundTotal).values(background_rows).on_conflict_do_nothing())
            db.commit()
        except Exception:
            db.rollback()
            raise

    def has_confidences(self, db: Session, username: str) -> bool:
        """Return whether the user has any confidence rows yet."""
        query = sa.select(sa.exists().where(UserFamilyConfidence.username == username))
        return db.execute(query).scalar()

    def get_all_confidences(self, db: Session, username: str) -> list[UserFamilyConfidence]:
        """Return every confidence row for the user, with its component loaded, ordered by family then slug."""
        query = (
            sa.select(UserFamilyConfidence)
            .join(UserFamilyConfidence.component)
            .options(contains_eager(UserFamilyConfidence.component))
            .where(UserFamilyConfidence.username == username)
            .order_by(UserFamilyConfidence.family, Component.slug)
        )
        return list(db.execute(query).scalars().all())

    def get_background_total(self, db: Session, username: str, family: SymptomFamily) -> float:
        """Return the user's background total for a family, or 0.0 if they have no row for it."""
        query = sa.select(UserBackgroundTotal.background_total).where(
            UserBackgroundTotal.username == username,
            UserBackgroundTotal.family == family.value,
        )
        total = db.execute(query).scalar_one_or_none()
        return total if total is not None else 0.0

    def get_confidences(
        self,
        db: Session,
        username: str,
        family: SymptomFamily,
        component_ids: list[UUID] | None = None,
    ) -> list[UserFamilyConfidence]:
        """Return the user's confidence rows for one family, optionally limited to the given components."""
        query = sa.select(UserFamilyConfidence).where(
            UserFamilyConfidence.username == username,
            UserFamilyConfidence.family == family.value,
        )
        if component_ids is not None:
            query = query.where(UserFamilyConfidence.component_id.in_(component_ids))
        return list(db.execute(query).scalars().all())

    def update_log_odds(
        self,
        db: Session,
        username: str,
        family: SymptomFamily,
        deltas: dict[UUID, float],
        commit: bool = True,
    ) -> None:
        """Add each delta to the matching component's log_odds for this family, in one transaction."""
        try:
            for component_id, delta in deltas.items():
                db.execute(
                    sa.update(UserFamilyConfidence)
                    .where(
                        UserFamilyConfidence.username == username,
                        UserFamilyConfidence.family == family.value,
                        UserFamilyConfidence.component_id == component_id,
                    )
                    .values(log_odds=UserFamilyConfidence.log_odds + delta)
                )
            if commit:
                db.commit()
        except Exception:
            db.rollback()
            raise

    def add_expected_reactions(
        self,
        db: Session,
        username: str,
        family: SymptomFamily,
        amounts: dict[UUID, float],
        commit: bool = True,
    ) -> None:
        """Add each amount to the matching component's expected_reactions for this family, in one transaction."""
        try:
            for component_id, amount in amounts.items():
                db.execute(
                    sa.update(UserFamilyConfidence)
                    .where(
                        UserFamilyConfidence.username == username,
                        UserFamilyConfidence.family == family.value,
                        UserFamilyConfidence.component_id == component_id,
                    )
                    .values(expected_reactions=UserFamilyConfidence.expected_reactions + amount)
                )
            if commit:
                db.commit()
        except Exception:
            db.rollback()
            raise

    def add_background_total(self, db: Session, username: str, family: SymptomFamily, amount: float) -> None:
        """Add an amount to the user's background total for a family."""
        try:
            db.execute(
                sa.update(UserBackgroundTotal)
                .where(
                    UserBackgroundTotal.username == username,
                    UserBackgroundTotal.family == family.value,
                )
                .values(background_total=UserBackgroundTotal.background_total + amount)
            )
            db.commit()
        except Exception:
            db.rollback()
            raise
