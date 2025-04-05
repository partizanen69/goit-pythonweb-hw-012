import asyncio
from typing import Generator, Any
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from main import app
from src.models.base import Base, User, UserRole
from src.database.db import get_db
from src.services.auth import AuthService
from src.services.redis_service import RedisService

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

test_user = {
    "username": "deadpool",
    "email": "deadpool@example.com",
    "password": "12345678",
}


# Mock Redis Service methods
@pytest.fixture(scope="module", autouse=True)
def mock_redis_service():
    """Mock Redis service for tests."""
    # Create a cache to simulate Redis storage
    redis_cache = {}

    # Create mock implementations
    async def mock_get(key: str) -> Any:
        return redis_cache.get(key)

    async def mock_set(key: str, value: Any, ttl: int = None) -> bool:
        redis_cache[key] = value
        return True

    async def mock_delete(key: str) -> bool:
        if key in redis_cache:
            del redis_cache[key]
            return True
        return False

    async def mock_close():
        redis_cache.clear()
        return True

    # Apply patches
    with patch.object(
        RedisService, "get", new=AsyncMock(side_effect=mock_get)
    ), patch.object(
        RedisService, "set", new=AsyncMock(side_effect=mock_set)
    ), patch.object(
        RedisService, "delete", new=AsyncMock(side_effect=mock_delete)
    ), patch.object(
        RedisService, "close", new=AsyncMock(side_effect=mock_close)
    ):
        yield


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            auth_service = AuthService(session)
            hash_password = auth_service.get_password_hash(test_user["password"])
            current_user = User(
                username=test_user["username"],
                email=test_user["email"],
                password=hash_password,
                email_verified=True,
                avatar_url="https://twitter.com/gravatar",
                role=UserRole.ADMIN,  # Set test user as admin
            )
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client() -> Generator[TestClient]:
    # Dependency override

    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception as err:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest_asyncio.fixture()
async def get_token():
    async with TestingSessionLocal() as session:
        auth_service = AuthService(session)
        token = auth_service.create_access_token(test_user.get("email"))
    return token
