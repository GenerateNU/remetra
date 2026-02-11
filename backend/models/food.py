"""Food database model."""

import uuid

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from database import Base


class Food(Base):
    """Food ORM model."""

    __tablename__ = "foods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    ingredients = Column(JSONB, nullable=True)  # JSON array of ingredients
    username = Column(String, nullable=True)  # Optional: if foods are user-specific
    created_at = Column(DateTime(timezone=True), server_default=func.now())
