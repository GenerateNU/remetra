import uuid

from sqlalchemy import Column, DateTime, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Tag(Base):
    """Tag ORM model."""

    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    llm_suggested = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    food_log_tags = relationship("FoodLogTag", back_populates="tag")


class FoodLogTag(Base):
    """Join table linking food logs to tags."""

    __tablename__ = "food_log_tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    food_log_id = Column(UUID(as_uuid=True), ForeignKey("food_logs.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tag = relationship("Tag", back_populates="food_log_tags")
    food_log = relationship("FoodLog", back_populates="food_log_tags")