"""Metrics database model."""

import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from database import Base


class Metrics(Base):
    """Metrics ORM model."""

    __tablename__ = "ingredient_symptom_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, ForeignKey("users.username", ondelete="CASCADE"), nullable=False)
    symptom_id = Column(UUID(as_uuid=True), ForeignKey("symptoms.id", ondelete="CASCADE"), nullable=False)
    ingredient = Column(String, nullable=False)

    # Algorithm output metrics
    exposures = Column(Integer, nullable=False)
    trigger_rate = Column(Float, nullable=False)
    base_rate = Column(Float, nullable=False)
    fishers_p_value = Column(Float, nullable=False)
    average_intensity = Column(Float, nullable=False)

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint("username", "symptom_id", "ingredient", name="uq_user_symptom_ingredient"),)
