"""Database models for the Contacts API.

This module defines the SQLAlchemy models for users and contacts.
"""

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Date, Text, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class Contact(Base):
    """Model representing a contact in the system.

    Attributes:
        id (int): Primary key
        first_name (str): Contact's first name
        last_name (str): Contact's last name
        email (str): Contact's email address
        phone (str): Contact's phone number
        birthday (Date): Contact's date of birth
        additional_data (str | None): Additional information about the contact
        user_id (int): Foreign key to the user who owns this contact
        user (User): Relationship to the user who owns this contact
    """
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    birthday: Mapped[Date] = mapped_column(Date, nullable=False)
    additional_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    user: Mapped["User"] = relationship("User", backref="contacts", lazy="joined")


class User(Base):
    """Model representing a user in the system.

    Attributes:
        id (int): Primary key
        username (str): User's display name
        email (str): User's email address
        password (str): Hashed password
        created_at (DateTime): Timestamp of user creation
        updated_at (DateTime): Timestamp of last update
        email_verified (bool): Whether the email has been verified
        verification_token (str | None): Token for email verification
        avatar_url (str | None): URL to user's avatar image
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), nullable=False, onupdate=func.now()
    )
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
