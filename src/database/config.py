"""Database configuration settings.

This module provides database connection configuration.
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Config:
    """Database configuration.

    This class defines the database connection URL.

    Attributes:
        DB_URL (str): Database connection URL in SQLAlchemy format
    """
    DB_URL = "postgresql+asyncpg://postgres:567234@localhost:5433/contacts_app"


config = Config()
