import uuid

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from database import Base


class Component(Base):
    """One row per taxonomy component (e.g. gluten, lactose), seeded from components.yaml."""

    __tablename__ = "components"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String, unique=True, nullable=False)
    display_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    definition = Column(Text)
    inclusion_confidence = Column(String, nullable=False)
    inclusion_rationale = Column(Text)
    sources = Column(JSONB, nullable=False, default=list)
    prior_tier = Column(String, nullable=False)
    flags = Column(JSONB, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
