"""Authentication routes for user registration and login."""

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.auth import LoginRequest, TokenResponse
from schemas.user import UserCreate, UserResponse
from services.auth_service import AuthService, decode_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Args:
        user_data: User registration data (username, email, password, etc.)
        db: Database session (injected by FastAPI)

    Returns:
        UserResponse: The created user without password

    Raises:
        HTTPException 400: If username or email already exists
    """
    service = AuthService()
    user = service.register_user(db, user_data)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with username and password.

    Args:
        credentials: Login credentials containing username and password
        db: Database session (injected by FastAPI)

    Returns:
        TokenResponse: Access token, token type, and username

    Raises:
        HTTPException 401: If credentials are invalid
    """
    service = AuthService()
    token_data = service.authenticate_user(db, credentials.username, credentials.password)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    return token_data


@router.get("/me", response_model=UserResponse)
async def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    """
    Get current authenticated user.

    Args:
        authorization: Authorization header with Bearer token (e.g., "Bearer <token>")
        db: Database session (injected by FastAPI)

    Returns:
        UserResponse: Current user data

    Raises:
        HTTPException 401: If token is invalid or user not found
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.replace("Bearer ", "")

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    service = AuthService()
    user = service.get_current_user(db, username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
