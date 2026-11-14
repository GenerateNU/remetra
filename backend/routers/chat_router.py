"""Chatbot routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from database import get_db
from routers.auth import get_current_user
from schemas.chat import ChatRequest, ChatResponse
from services.chat_service import ChatError, ChatService

router = APIRouter(prefix="/chat", tags=["Chat"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=ChatResponse)
async def ask_chatbot(
    payload: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    """Answer the authenticated user's question about their own logs. Nothing is persisted."""
    chat_service = ChatService()
    try:
        # ask() makes blocking DB and Gemini calls; running it in a worker thread keeps the event loop free
        # for other requests. run_in_threadpool copies the request context, so current_username carries over.
        return await run_in_threadpool(chat_service.ask, db, payload.question)
    except ChatError as e:
        raise HTTPException(status_code=502, detail=str(e))
