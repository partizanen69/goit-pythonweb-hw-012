from typing import Optional
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
import uuid

from src.database.db import get_db
from src.models.base import User
from src.schemas.user import UserCreate
from src.conf.config import settings
from src.utils.auth import verify_password, get_password_hash, create_access_token
from src.services.email import EmailService
from src.repository.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)
        self.email_service = EmailService()

    async def register(self, user_data: UserCreate) -> User:
        # Check if user exists
        existing_user = await self.repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        verification_token = str(uuid.uuid4())

        new_user = await self.repository.create(
            {
                "username": user_data.username,
                "email": user_data.email,
                "password": hashed_password,
                "verification_token": verification_token,
            }
        )

        # Send verification email
        await self.email_service.send_verification_email(
            new_user.email, new_user.username, verification_token
        )

        return new_user

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = await self.repository.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    async def verify_email(self, token: str):
        user = await self.repository.get_by_verification_token(token)

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

        return {"message": "Email verified successfully"}

    @staticmethod
    async def get_current_user(
        token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
    ) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        repository = UserRepository(db)
        user = await repository.get_by_email(email)

        if user is None:
            raise credentials_exception

        return user
