"""User management service for the Contacts API.

This module provides functionality for managing user profiles and avatars.
"""

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.services.auth import AuthService
from src.repository.user_repository import UserRepository
from src.services.cloud_image import CloudImage
from src.models.base import User, UserRole


class UserService:
    """Service for managing user profiles.

    This class provides methods for managing user data and avatars.
    """

    def __init__(self, db: AsyncSession):
        """Initialize the user service.

        Args:
            db (AsyncSession): Database session
        """
        self.repository = UserRepository(db)

    async def update_avatar(self, user: User, file: UploadFile) -> User:
        """Update a user's avatar image.

        Args:
            user (User): User to update
            file (UploadFile): Image file to upload

        Returns:
            User: Updated user data with new avatar URL

        Raises:
            HTTPException: If file is not an image or user lacks permission
        """
        # Check if user has permission to change avatar
        if user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can change their avatar",
            )

        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image"
            )

        public_id = f"ContactsApp/{user.id}"

        content = await file.read()

        result = await CloudImage.upload(content, public_id=public_id)

        updated_user = await self.repository.update_avatar(user, result["secure_url"])
        await AuthService.invalidate_user_cache(user.email)
        return updated_user

    async def update_user_role(self, user_id: int, role: UserRole) -> User:
        """Update a user's role.

        Args:
            user_id (int): ID of the user to update
            role (UserRole): New role for the user

        Returns:
            User: Updated user object

        Raises:
            HTTPException: If user not found
        """
        # First, get the user by ID
        query = select(User).filter(User.id == user_id)
        result = await self.repository.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )

        # Update the user's role
        updated_user = await self.repository.update_role(user, role)
        await AuthService.invalidate_user_cache(user.email)
        return updated_user
