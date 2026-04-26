"""Schemas for algorithm symptom-food association endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class KeyMetrics(BaseModel):
    """JSON payload matching IngredientSymptomMetrics fields."""

    exposures: int = Field(..., ge=0)
    trigger_rate: float = Field(..., ge=0)
    base_rate: float = Field(..., ge=0)
    fishers_p_value: float = Field(..., ge=0)
    average_intensity: float = Field(..., ge=0)


class AlgorithmAssociationResponse(BaseModel):
    """Response schema for one symptom-ingredient association row."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: str
    symptom_id: UUID
    ingredient_name: str
    key_metrics: KeyMetrics
    updated_at: datetime


class AlgorithmRunRequest(BaseModel):
    """Request payload for running and persisting algorithm associations."""

    user_id: str = Field(..., description="User identifier")
    symptom_ids: list[UUID] = Field(default=[], description="Optional symptom IDs to scope the algorithm")
    time_window_hours: float = Field(
        default=4.0,
        ge=0.0,
        description="Hours before each symptom to consider food exposures",
    )


class AlgorithmRunResponse(BaseModel):
    """Response payload after algorithm run and persistence."""

    associations: list[AlgorithmAssociationResponse]
