from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.base import User
from src.schemas.user import UserCreate


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(User).filter(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email_verification_token(self, token: str) -> Optional[User]:
        query = select(User).filter(User.verification_token == token)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, user_data: dict) -> User:
        new_user = User(**user_data)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def update(self, user: User) -> User:
        await self.db.commit()
        return user

    async def update_avatar(self, user: User, avatar_url: str) -> User:
        user.avatar_url = avatar_url
        await self.db.commit()
        await self.db.refresh(user)
        return user
