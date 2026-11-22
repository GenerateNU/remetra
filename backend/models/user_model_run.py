"""Database model for when the nightly model last ran for a user."""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from database import Base


class UserModelRun(Base):
    """One row per user: the end of the last window the nightly run observed (t_last in the model v2 spec)."""

    __tablename__ = "user_model_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, ForeignKey("users.username", ondelete="CASCADE"), nullable=False, unique=True)
    last_update = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
