"""Database model for a user's per-family background symptom totals."""

import uuid

from sqlalchemy import CheckConstraint, Column, DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from database import Base
from models.symptom_family import FAMILY_VALUES


class UserBackgroundTotal(Base):
    """One row per user per symptom family, tracking how many symptoms were put down to background."""

    __tablename__ = "user_background_totals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, ForeignKey("users.username", ondelete="CASCADE"), nullable=False)
    family = Column(String, nullable=False)
    background_total = Column(Float, nullable=False, default=0.0, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("username", "family", name="uq_user_background_totals_user_family"),
        CheckConstraint(f"family IN ({FAMILY_VALUES})", name="ck_user_background_totals_family"),
    )
