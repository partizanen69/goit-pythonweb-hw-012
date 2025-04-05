"""User management routes for the Contacts API.

This module provides endpoints for managing user profiles and avatars.
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.services.user import UserService
from src.services.auth import AuthService
from src.models.base import User, UserRole
from src.schemas.user import UserResponse

# Define a new schema for updating user role
from pydantic import BaseModel


class RoleUpdate(BaseModel):
    """Schema for updating a user's role.

    Attributes:
        user_id (int): User's ID
        role (str): New role for the user (USER, ADMIN)
    """

    user_id: int
    role: str


router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
) -> User:
    """Update user's avatar image.

    Args:
        file (UploadFile): Image file to upload
        db (AsyncSession): Database session
        current_user (User): Current authenticated user

    Returns:
        User: Updated user data with new avatar URL

    Raises:
        HTTPException: If file upload fails or file type is not supported
    """
    user_service = UserService(db)
    return await user_service.update_avatar(current_user, file)


@router.post("/role", response_model=UserResponse)
async def update_role(
    role_update: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
) -> User:
    """Update a user's role. Only admins can use this endpoint.

    Args:
        role_update (RoleUpdate): Role update data
        db (AsyncSession): Database session
        current_user (User): Current authenticated user

    Returns:
        User: Updated user data

    Raises:
        HTTPException: If current user is not an admin or specified role is invalid
    """
    # Check if current user is an admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can change user roles",
        )

    # Validate role
    try:
        new_role = UserRole(role_update.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Valid roles are: {[role.value for role in UserRole]}",
        )

    user_service = UserService(db)
    return await user_service.update_user_role(role_update.user_id, new_role)
