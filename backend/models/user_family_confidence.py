"""Database model for a user's family-component confidence scores."""

import uuid

from sqlalchemy import CheckConstraint, Column, DateTime, Float, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base
from models.symptom_family import FAMILY_VALUES


class UserFamilyConfidence(Base):
    """One row per user per component per symptom family, holding the model's evidence for that link."""

    __tablename__ = "user_family_confidences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, ForeignKey("users.username", ondelete="CASCADE"), nullable=False)
    component_id = Column(UUID(as_uuid=True), ForeignKey("components.id", ondelete="CASCADE"), nullable=False)
    family = Column(String, nullable=False)
    log_odds = Column(Float, nullable=False)
    expected_reactions = Column(Float, nullable=False, default=0.0, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    component = relationship("Component")

    __table_args__ = (
        UniqueConstraint("username", "component_id", "family", name="uq_user_family_confidences_user_component_family"),
        CheckConstraint(f"family IN ({FAMILY_VALUES})", name="ck_user_family_confidences_family"),
        Index("ix_user_family_confidences_username_family", "username", "family"),
    )
