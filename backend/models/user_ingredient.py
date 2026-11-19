"""User ingredient preference database model."""

import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from database import Base


class IngredientPreference(str, enum.Enum):
    """How a user feels about an ingredient."""

    AVOID = "AVOID"
    SUSPECT = "SUSPECT"
    SAFE = "SAFE"


class UserIngredient(Base):
    """One row per user per ingredient, recording which category the user put it in."""

    __tablename__ = "user_ingredients"
    __table_args__ = (UniqueConstraint("username", "ingredient_id", name="uq_user_ingredient_user_ingredient"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, ForeignKey("users.username", ondelete="CASCADE"), nullable=False)
    ingredient_id = Column(UUID(as_uuid=True), ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False)
    preference = Column(Enum(IngredientPreference, name="ingredient_preference"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())