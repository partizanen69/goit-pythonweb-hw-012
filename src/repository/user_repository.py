"""Repository for user-related database operations.

This module provides database access methods for user CRUD operations
and specialized queries.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.base import User, UserRole


class UserRepository:
    """Repository for managing users in the database.

    This class provides methods for creating, reading, and updating users,
    as well as specialized queries like finding users by email or verification token.
    """

    def __init__(self, db: AsyncSession):
        """Initialize the user repository.

        Args:
            db (AsyncSession): Database session
        """
        self.db = db

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by their email address.

        Args:
            email (str): Email address to search for

        Returns:
            Optional[User]: User object if found, None otherwise
        """
        query = select(User).filter(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email_verification_token(self, token: str) -> Optional[User]:
        """Get a user by their email verification token.

        Args:
            token (str): Email verification token to search for

        Returns:
            Optional[User]: User object if found, None otherwise
        """
        query = select(User).filter(User.verification_token == token)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_reset_password_token(self, token: str) -> Optional[User]:
        """Get a user by their password reset token.

        Args:
            token (str): Password reset token to search for

        Returns:
            Optional[User]: User object if found, None otherwise
        """
        query = select(User).filter(User.reset_password_token == token)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, user_data: dict) -> User:
        """Create a new user in the database.

        Args:
            user_data (dict): User data including username, email, and hashed password

        Returns:
            User: Created user object
        """
        new_user = User(**user_data)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def update(self, user: User) -> User:
        """Update a user in the database.

        Args:
            user (User): User object with updated data

        Returns:
            User: Updated user object
        """
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_avatar(self, user: User, avatar_url: str) -> User:
        """Update a user's avatar URL.

        Args:
            user (User): User to update
            avatar_url (str): New avatar URL

        Returns:
            User: Updated user object
        """
        user.avatar_url = avatar_url
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_password(self, user: User, hashed_password: str) -> User:
        """Update a user's password.

        Args:
            user (User): User to update
            hashed_password (str): New hashed password

        Returns:
            User: Updated user object
        """
        user.password = hashed_password
        user.reset_password_token = None
        user.reset_token_expires = None
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_role(self, user: User, role: UserRole) -> User:
        """Update a user's role.

        Args:
            user (User): User to update
            role (UserRole): New role for the user

        Returns:
            User: Updated user object
        """
        user.role = role
        await self.db.commit()
        await self.db.refresh(user)
        return user
