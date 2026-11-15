"""Symptom database model."""

import uuid

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base
from models.symptom_family import SymptomFamily

FAMILY_VALUES = ", ".join(f"'{family}'" for family in SymptomFamily)  # 'GI', 'SKIN', 'HEAD'


class Symptom(Base):
    """Symptom ORM model."""

    __tablename__ = "symptoms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, ForeignKey("users.username", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    sensation = Column(String, nullable=False)
    family = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    symptom_logs = relationship("SymptomLog", back_populates="symptom")

    __table_args__ = (
        UniqueConstraint(
            "username",
            "location",
            "sensation",
            name="uq_symptoms_username_location_sensation",
        ),
        CheckConstraint(f"family IN ({FAMILY_VALUES})", name="ck_symptoms_family"),
    )
