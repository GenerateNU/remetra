"""Ingredient pool database model."""

import uuid

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from database import Base


class IngredientPool(Base):
    """One stored ingredient pool per user per UTC date."""

    __tablename__ = "ingredient_pools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, ForeignKey("users.username", ondelete="CASCADE"), nullable=False)
    pool_date = Column(Date, nullable=False)
    ingredient_ids = Column(JSONB, nullable=False)
    washout = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (UniqueConstraint("username", "pool_date", name="uq_ingredient_pool_user_date"),)
