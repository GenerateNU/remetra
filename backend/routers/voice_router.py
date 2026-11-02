"""Voice parse routes."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from routers.auth import get_current_user
from schemas.user import UserResponse
from schemas.voice import VoiceParseResponse
from services.voice_parse_service import VoiceParseError, VoiceParseService

router = APIRouter(prefix="/voice", tags=["Voices"], dependencies=[Depends(get_current_user)])


@router.post("/parse", response_model=VoiceParseResponse)
async def parse_voice(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user),
) -> VoiceParseResponse:
    """Get voice parse for authenticated user"""

    audio_bytes = file.file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Audio file is empty")

    mime_type = file.content_type or "audio/mp4"

    voice_parse_service = VoiceParseService()
    try:
        return voice_parse_service.parse(audio_bytes, mime_type)
    except VoiceParseError as e:
        raise HTTPException(status_code=502, detail=str(e))
