"""Symptom log database model."""

import uuid

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from database import Base


class SymptomLog(Base):
    """Symptom log ORM model."""

    __tablename__ = "symptom_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, ForeignKey("users.username", ondelete="CASCADE"), nullable=False)
    symptom_id = Column(UUID(as_uuid=True), ForeignKey("symptoms.id", ondelete="CASCADE"), nullable=False)
    intensity = Column(Integer, CheckConstraint("intensity >= 1 AND intensity <= 10"), nullable=False)
    duration = Column(Integer, nullable=True)  # duration in minutes
    timestamp = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
