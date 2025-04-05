"""Authentication service for the Contacts API.

This module provides authentication-related functionality including user registration,
login, email verification, and JWT token management.
"""

from typing import Optional
from datetime import UTC, datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
import uuid
from passlib.context import CryptContext

from src.database.db import get_db
from src.models.base import User, UserRole
from src.schemas.user import UserCreate
from src.conf.config import settings
from src.services.email import EmailService
from src.services.redis_service import RedisService
from src.repository.user_repository import UserRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for handling user authentication and authorization.

    This class provides methods for user registration, authentication,
    email verification, and JWT token management.
    """

    def __init__(self, db: AsyncSession):
        """Initialize the authentication service.

        Args:
            db (AsyncSession): Database session
        """
        self.repository = UserRepository(db)
        self.email_service = EmailService()

    async def register(self, user_data: UserCreate) -> User:
        """Register a new user.

        Args:
            user_data (UserCreate): User registration data

        Returns:
            User: Created user object

        Raises:
            HTTPException: If email is already registered
        """
        # Check if user exists
        existing_user = await self.repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )

        # Create new user
        hashed_password = self.get_password_hash(user_data.password)
        email_verification_token = str(uuid.uuid4())

        new_user = await self.repository.create(
            {
                "username": user_data.username,
                "email": user_data.email,
                "password": hashed_password,
                "verification_token": email_verification_token,
                "role": UserRole.USER,  # Default role is USER
            }
        )

        # Send verification email
        await self.email_service.send_verification_email(
            new_user.email, new_user.username, email_verification_token
        )

        return new_user

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password.

        Args:
            email (str): User's email address
            password (str): User's password

        Returns:
            Optional[User]: User object if authentication successful, None otherwise
        """
        user = await self.repository.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.password):
            return None

        # Cache the user after successful authentication
        cache_key = f"user:{user.email}"
        await RedisService.set(cache_key, user)

        return user

    async def verify_email(self, token: str):
        """Verify a user's email address.

        Args:
            token (str): Email verification token

        Returns:
            dict: Success message

        Raises:
            HTTPException: If token is invalid or email already verified
        """
        user = await self.repository.get_by_email_verification_token(token)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid verification token",
            )

        if user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified"
            )

        user.email_verified = True
        user.verification_token = None
        await self.repository.update(user)
        await AuthService.invalidate_user_cache(user.email)

        # Update user in cache if exists
        cache_key = f"user:{user.email}"
        await RedisService.set(cache_key, user)

        return {"message": "Email verified successfully"}

    async def request_password_reset(self, email: str):
        """Request a password reset.

        Args:
            email (str): Email address to reset password for

        Returns:
            dict: Success message

        Raises:
            HTTPException: If user not found
        """
        user = await self.repository.get_by_email(email)
        if not user:
            # Return success even if email doesn't exist to prevent user enumeration
            return {
                "message": "If your email is registered, you will receive a password reset link"
            }

        # Generate and store reset token
        reset_token = str(uuid.uuid4())
        user.reset_password_token = reset_token
        user.reset_token_expires = (
            datetime.now(timezone.utc) + timedelta(hours=24)
        ).replace(tzinfo=None)
        await self.repository.update(user)

        # Invalidate user cache
        await AuthService.invalidate_user_cache(user.email)

        # Send reset email
        await self.email_service.send_password_reset_email(
            user.email, user.username, reset_token
        )

        return {
            "message": "If your email is registered, you will receive a password reset link"
        }

    async def reset_password(self, token: str, new_password: str):
        """Reset a user's password.

        Args:
            token (str): Password reset token
            new_password (str): New password

        Returns:
            dict: Success message

        Raises:
            HTTPException: If token is invalid or expired
        """
        user = await self.repository.get_by_reset_password_token(token)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid reset token",
            )

        # Check if token has expired
        if user.reset_token_expires and user.reset_token_expires < datetime.now(
            timezone.utc
        ).replace(tzinfo=None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired",
            )

        # Update password
        hashed_password = self.get_password_hash(new_password)
        await self.repository.update_password(user, hashed_password)

        # Invalidate user cache
        await AuthService.invalidate_user_cache(user.email)

        return {"message": "Password reset successfully"}

    def create_access_token(
        self, user_email: str, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token.

        Args:
            user_email (str): User's email address
            expires_delta (Optional[timedelta]): Token expiration time

        Returns:
            str: JWT access token
        """
        to_encode: dict[str, str | float] = {"sub": user_email}

        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=15)

        to_encode.update({"exp": expire.timestamp()})

        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    async def get_current_user(
        token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
    ) -> User:
        """Get the current authenticated user from a JWT token.

        Args:
            token (str): JWT access token
            db (AsyncSession): Database session

        Returns:
            User: Current authenticated user

        Raises:
            HTTPException: If token is invalid or user not found
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            email: str | None = payload.get("sub")
            if email is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        # Try to get user from Redis cache first
        cache_key = f"user:{email}"
        cached_user = await RedisService.get(cache_key)

        if cached_user:
            return cached_user

        # If not in cache, get from database
        repository = UserRepository(db)
        user = await repository.get_by_email(email)

        if user is None:
            raise credentials_exception

        # Cache the user for future requests
        await RedisService.set(cache_key, user)

        return user

    @staticmethod
    async def invalidate_user_cache(email: str) -> bool:
        """Invalidate a user's cache entry.

        This method should be called whenever a user's data is modified.

        Args:
            email (str): User's email address

        Returns:
            bool: True if cache was invalidated, False otherwise
        """
        cache_key = f"user:{email}"
        return await RedisService.delete(cache_key)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.

        Args:
            plain_password (str): Plain text password to verify
            hashed_password (str): Hashed password to verify against

        Returns:
            bool: True if password matches hash, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate a hash from a password.

        Args:
            password (str): Password to hash

        Returns:
            str: Hashed password
        """
        return pwd_context.hash(password)
