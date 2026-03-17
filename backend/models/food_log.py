"""Food log database model."""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class FoodLog(Base):
    """Food log ORM model."""

    __tablename__ = "food_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, ForeignKey("users.username", ondelete="CASCADE"), nullable=False)
    food_id = Column(UUID(as_uuid=True), ForeignKey("foods.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(String, nullable=True)  # "1 cup", "2 slices", etc
    timestamp = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    food = relationship("Food", back_populates="food_logs")
    food_log_tags = relationship("FoodLogTag", back_populates="food_log")
