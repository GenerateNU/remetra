import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from database import Base


class UserComponentState(Base):
    """Per-user learned state for one component-family pair, updated nightly."""

    __tablename__ = "user_component_states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, ForeignKey("users.username", ondelete="CASCADE"), nullable=False)
    component_id = Column(UUID(as_uuid=True), ForeignKey("components.id", ondelete="CASCADE"), nullable=False)
    family = Column(String, nullable=False)

    log_odds = Column(Float, nullable=False)
    expected_reactions = Column(Float, nullable=False, default=0.0)
    exposure_count = Column(Integer, nullable=False, default=0)
    background_rate = Column(Float, nullable=False)
    background_total = Column(Float, nullable=False, default=0.0)
    hours_since_onboarding = Column(Float, nullable=False, default=0.0)
    last_update = Column(DateTime(timezone=True), server_default=func.now())

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("username", "component_id", "family", name="uq_user_component_family"),
    )
