"""Authentication routes for the Contacts API.

This module provides endpoints for user registration, login, email verification,
and user profile access.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
import uuid

from src.models.base import User
from src.database.db import get_db
from src.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from src.schemas.user import PasswordResetRequest, PasswordReset
from src.services.auth import AuthService
from src.conf.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user.

    Args:
        user (UserCreate): User registration data
        db (AsyncSession): Database session

    Returns:
        UserResponse: Created user data

    Raises:
        HTTPException: If user with this email already exists
    """
    auth_service = AuthService(db)
    return await auth_service.register(user)


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return access token.

    Args:
        user_data (UserLogin): User login credentials
        db (AsyncSession): Database session

    Returns:
        TokenResponse: Access token and token type

    Raises:
        HTTPException: If credentials are invalid or email is not verified
    """
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        user.email, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/verify/{token}")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    """Verify user's email address.

    Args:
        token (str): Email verification token
        db (AsyncSession): Database session

    Returns:
        dict: Verification status message

    Raises:
        HTTPException: If token is invalid or expired
    """
    auth_service = AuthService(db)
    return await auth_service.verify_email(token)


@router.post("/request-password-reset")
async def request_password_reset(
    request_data: PasswordResetRequest, db: AsyncSession = Depends(get_db)
):
    """Request a password reset.

    Args:
        request_data (PasswordResetRequest): Password reset request data
        db (AsyncSession): Database session

    Returns:
        dict: Success message
    """
    auth_service = AuthService(db)
    return await auth_service.request_password_reset(request_data.email)


@router.post("/reset-password/{token}")
async def reset_password(
    token: str, password_data: PasswordReset, db: AsyncSession = Depends(get_db)
):
    """Reset a user's password.

    Args:
        token (str): Password reset token
        password_data (PasswordReset): New password data
        db (AsyncSession): Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If token is invalid or expired
    """
    auth_service = AuthService(db)
    return await auth_service.reset_password(token, password_data.password)


def get_user_identifier(request: Request) -> str:
    """Get user identifier for rate limiting.

    Args:
        request (Request): FastAPI request object

    Returns:
        str: User ID if authenticated, otherwise remote address
    """
    user: User | None = getattr(request.state, "current_user", None)
    return str(user.id) if user else get_remote_address(request)


limiter = Limiter(key_func=get_user_identifier)


@router.get("/me", response_model=UserResponse)
@limiter.limit("5/minute")
async def read_users_me(
    request: Request, current_user=Depends(AuthService.get_current_user)
) -> User:
    """Get current user's profile.

    Args:
        request (Request): FastAPI request object
        current_user (User): Current authenticated user

    Returns:
        User: Current user's profile data

    Raises:
        HTTPException: If user is not authenticated
    """
    return current_user
