"""Authentication routes for user registration and login."""

from clerk_backend_api import authenticate_request_async
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import get_db
from schemas.user import UserResponse, UserUpdate
from services.auth_service import AuthService, clerk_auth_options

router = APIRouter(prefix="/auth", tags=["Authentication"])

http_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    _credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer),
) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    state = await authenticate_request_async(request, clerk_auth_options())
    if not state.is_signed_in or not state.payload:
        raise credentials_exception

    clerk_user_id = state.payload.get("sub")
    if not clerk_user_id:
        raise credentials_exception

    return AuthService().resolve_user(db, clerk_user_id)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return AuthService().update_user(db, current_user.username, user_update)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
