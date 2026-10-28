from pydantic import BaseModel, ConfigDict


class VoiceBase(BaseModel):
    """Schema for voice food logs."""

    transcript: str = ""
    name: str = ""
    ingredients: list[str] = []


class VoiceParseResponse(VoiceBase):
    """Voice parse response"""

    model_config = ConfigDict(from_attributes=True)
