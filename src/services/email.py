from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from src.conf.config import settings
from pathlib import Path


class EmailService:
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
        print(self.config)
        self.fast_mail = FastMail(self.config)

    async def send_verification_email(self, email: str, username: str, token: str):
        message = MessageSchema(
            subject="Verify your email",
            recipients=[email],
            body=f"Hi {username}, please verify your email by clicking on this link: "
            f"http://localhost:8000/api/auth/verify/{token}",
            subtype="html",
        )

        await self.fast_mail.send_message(message)
