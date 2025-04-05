"""Application configuration settings.

This module loads and provides access to configuration settings from environment variables.
"""

from pydantic import SecretStr
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    """Application configuration settings.

    This class defines all configuration settings for the application,
    loading them from environment variables with fallback default values.

    Attributes:
        DB_URL (str): Database connection URL
        SECRET_KEY (str): Secret key for JWT token generation
        ALGORITHM (str): Algorithm used for JWT token generation
        ACCESS_TOKEN_EXPIRE_MINUTES (int): JWT token expiration time in minutes
        MAIL_USERNAME (str): SMTP server username
        MAIL_PASSWORD (SecretStr): SMTP server password
        MAIL_FROM (str): Email sender address
        MAIL_PORT (int): SMTP server port
        MAIL_SERVER (str): SMTP server hostname
        CLOUDINARY_NAME (str): Cloudinary cloud name
        CLOUDINARY_API_KEY (str): Cloudinary API key
        CLOUDINARY_API_SECRET (str): Cloudinary API secret
        REDIS_HOST (str): Redis server hostname
        REDIS_PORT (int): Redis server port
        REDIS_PASSWORD (str): Redis password
        REDIS_USER_CACHE_TTL (int): TTL for cached user data in seconds
    """

    # database
    DB_URL: str = os.getenv("DATABASE_URL", "")
    # jwt
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # email
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: SecretStr = SecretStr(os.getenv("MAIL_PASSWORD", ""))
    MAIL_FROM: str = os.getenv("MAIL_FROM", "")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", "465"))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.meta.ua")

    # Cloudinary settings
    CLOUDINARY_NAME: str = os.getenv("CLOUDINARY_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")

    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_USER_CACHE_TTL: int = int(os.getenv("REDIS_USER_CACHE_TTL", "3600"))  # 1 hour


settings = Settings()
