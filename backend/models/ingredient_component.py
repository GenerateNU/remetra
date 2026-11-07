import uuid

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from database import Base


class IngredientComponent(Base):
    """One row per ingredient-component pairing (e.g. wheat bread - gluten), seeded from ingredient_components.csv."""

    __tablename__ = "ingredient_components"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ingredient_id = Column(UUID(as_uuid=True), ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False)
    component_id = Column(UUID(as_uuid=True), ForeignKey("components.id", ondelete="CASCADE"), nullable=False)
    concentration_level = Column(Integer, nullable=False)
    confidence = Column(String, nullable=False)
    rationale = Column(Text)
    source = Column(String)
    concentration_basis = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("ingredient_id", "component_id", name="uq_ingredient_id_component_id"),
        CheckConstraint("concentration_level BETWEEN 0 AND 3", name="ck_concentration_level_range"),
    )
