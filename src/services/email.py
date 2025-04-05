"""Email service for the Contacts API.

This module provides functionality for sending emails, including email verification.
"""

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from src.conf.config import settings
from pathlib import Path


class EmailService:
    """Service for sending emails.

    This class provides methods for sending various types of emails,
    including email verification.
    """

    config = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_FROM_NAME="Example email",
        MAIL_STARTTLS=False,
        MAIL_SSL_TLS=True,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )

    def __init__(self):
        """Initialize the email service with FastMail configuration."""
        self.fast_mail = FastMail(self.config)

    async def send_verification_email(self, email: str, username: str, token: str):
        """Send an email verification link to a user.

        Args:
            email (str): User's email address
            username (str): User's display name
            token (str): Email verification token
        """
        message = MessageSchema(
            subject="Verify your email",
            recipients=[email],
            body=f"Hi {username}, please verify your email by clicking on this link: "
            f"http://localhost:8000/api/auth/verify/{token}",
            subtype=MessageType.html,
        )

        await self.fast_mail.send_message(message)

    async def send_password_reset_email(self, email: str, username: str, token: str):
        """Send a password reset link to a user.

        Args:
            email (str): User's email address
            username (str): User's display name
            token (str): Password reset token
        """
        message = MessageSchema(
            subject="Reset at contacts app",
            recipients=[email],
            body=f"Hi {username}, you requested to reset. "
            f"Please click on this link to reset: "
            f"http://localhost:8000/api/auth/reset-password/{token} "
            f"If you didn't request this, please ignore this email.",
            subtype=MessageType.html,
        )

        await self.fast_mail.send_message(message)
