import uuid

from sqlalchemy import Column, DateTime, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from database import Base


class Symptom(Base):
    """Symptom ORM model."""

    __tablename__ = "symptoms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String, unique=True, nullable=False)

    description = Column(String, nullable=True)

    severity = Column(Integer, nullable=True)  
    # Example: 1–10 scale or similar business meaning

    username = Column(String, nullable=True)  
    # Optional: if symptoms are user-specific

    created_at = Column(DateTime(timezone=True), server_default=func.now())
