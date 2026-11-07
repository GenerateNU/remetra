import uuid

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func


from database import Base


class Ingredient(Base):
    """Ingredient from taxonomy dataset"""

    __tablename__ = "ingredients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String, unique=True, nullable=False)
    canonical_name = Column(String, nullable=False)
    aliases = Column(String, nullable=True)
    groups = Column(String, nullable=True)
    std_serving_g = Column(Integer, nullable=True)
    fat_g_per_100g = Column(Float, nullable=True)
    fiber_g_per_100g = Column(Float, nullable=True)
    mapping_confidence = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())