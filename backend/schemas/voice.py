from pydantic import BaseModel

class VoiceBase(BaseModel):
    """Schema for voice food logs."""

    transcript: str = None
    name: str = None
    ingredients: list[str] = None

class VoiceParseResponse(VoiceBase):
    """ Voice parse response """