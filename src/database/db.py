"""Database session management.

This module provides functionality for managing database sessions and connections.
"""

import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.database.config import config


class DatabaseSessionManager:
    """Manager for database sessions.

    This class provides functionality for creating and managing database sessions.
    It ensures proper handling of session lifecycle and error handling.
    """

    def __init__(self, url: str):
        """Initialize the database session manager.

        Args:
            url (str): Database connection URL
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """Create a new database session.

        This is an async context manager that yields a database session
        and handles proper cleanup and error handling.

        Yields:
            AsyncSession: Database session

        Raises:
            Exception: If database session is not initialized
            SQLAlchemyError: If a database error occurs
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise  # Re-raise the original error
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(config.DB_URL)


async def get_db():
    """Get a database session.

    This is a dependency that can be used in FastAPI endpoints
    to get a database session.

    Yields:
        AsyncSession: Database session
    """
    async with sessionmanager.session() as session:
        yield session

