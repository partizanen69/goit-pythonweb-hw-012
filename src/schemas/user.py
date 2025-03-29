"""Pydantic schemas for user data validation.

This module defines the data validation schemas for user-related operations.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# ... means required
class UserCreate(BaseModel):
    """Schema for creating a new user.

    Attributes:
        username (str): User's display name (3-50 characters)
        email (EmailStr): User's email address
        password (str): User's password (6-50 characters)
    """
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=50)


class UserResponse(BaseModel):
    """Schema for user response data.

    Attributes:
        id (int): User's unique identifier
        username (str): User's display name
        email (str): User's email address
        email_verified (bool): Whether the email has been verified
        created_at (datetime): User creation timestamp
        avatar_url (Optional[str]): URL to user's avatar image
    """
    id: int
    username: str
    email: str
    email_verified: bool
    created_at: datetime
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login credentials.

    Attributes:
        email (EmailStr): User's email address
        password (str): User's password
    """
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for authentication token response.

    Attributes:
        access_token (str): JWT access token
        token_type (str): Token type (always "bearer")
    """
    access_token: str
    token_type: str = "bearer"
