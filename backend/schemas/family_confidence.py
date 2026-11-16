from pydantic import BaseModel, ConfigDict


class FamilyConfidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    component_slug: str
    family: str
    confidence: float


class ComponentConfidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    component_slug: str
    confidence: float
