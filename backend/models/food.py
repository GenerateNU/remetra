"""Food database model."""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Food(Base):
    """Food ORM model."""

    __tablename__ = "foods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    ingredients = Column(JSONB, nullable=True)
    username = Column(String, ForeignKey("users.username", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    food_tags = relationship("FoodTag", back_populates="food", cascade="all, delete-orphan", passive_deletes=True)
    food_logs = relationship("FoodLog", back_populates="food", cascade="all, delete-orphan", passive_deletes=True)
    tags = relationship("Tag", secondary="food_tags", lazy="select", viewonly=True)

    __table_args__ = (UniqueConstraint("name", "username"),)
