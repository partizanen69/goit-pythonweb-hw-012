"""Pydantic schemas for contact data validation.

This module defines the data validation schemas for contact-related operations.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date


# ... means required field
class ContactBase(BaseModel):
    """Base schema for contact data validation.

    Attributes:
        first_name (str): Contact's first name (1-50 characters)
        last_name (str): Contact's last name (1-50 characters)
        email (EmailStr): Contact's email address
        phone (str): Contact's phone number (5-20 characters)
        birthday (date): Contact's date of birth
        additional_data (Optional[str]): Additional information (max 500 characters)
    """
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone: str = Field(..., min_length=5, max_length=20)
    birthday: date
    additional_data: Optional[str] = Field(None, max_length=500)


class ContactCreate(ContactBase):
    """Schema for creating a new contact.

    Inherits all fields from ContactBase.
    """
    pass


class ContactUpdate(BaseModel):
    """Schema for updating an existing contact.

    All fields are optional, allowing partial updates.

    Attributes:
        first_name (Optional[str]): Contact's first name (1-50 characters)
        last_name (Optional[str]): Contact's last name (1-50 characters)
        email (Optional[EmailStr]): Contact's email address
        phone (Optional[str]): Contact's phone number (5-20 characters)
        birthday (Optional[date]): Contact's date of birth
        additional_data (Optional[str]): Additional information (max 500 characters)
    """
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=5, max_length=20)
    birthday: Optional[date] = None
    additional_data: Optional[str] = Field(None, max_length=500)


class ContactResponse(ContactBase):
    """Schema for contact response data.

    Inherits all fields from ContactBase and adds an ID field.

    Attributes:
        id (int): Contact's unique identifier
    """
    id: int

    class Config:
        from_attributes = True
