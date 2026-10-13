"""Authentication routes for symptom CRUD."""

from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_user
from schemas.voice import VoiceParseResponse
from schemas.user import UserResponse
from services.voice_parse_service import VoiceParseService, VoiceParseError

router = APIRouter(
    prefix="/voice",
    tags=["Voices"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/parse", response_model=VoiceParseResponse)
async def get_voice_parse(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user),
) -> VoiceParseResponse:
    """Get voice parse for authenticated user"""

    audio_bytes = file.file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Audio file is empty")

    mime_type = file.content_type or "audio/mp4"

    voice_parse_service = VoiceParseService()
    voice_transcript = voice_parse_service.parse(audio_bytes, mime_type)

    try:
        return voice_transcript
    except VoiceParseError as e:
        raise HTTPException(status_code=502, detail=str(e))