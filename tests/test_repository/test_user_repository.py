import pytest
from unittest.mock import AsyncMock, Mock
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.base import User
from src.repository.user_repository import UserRepository


@pytest.fixture
def mock_session() -> AsyncSession:
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = Mock()
    return session


@pytest.fixture
def test_user():
    return User(
        id=1,
        username="test_user",
        email="test@example.com",
        password="hashed_password",
        verification_token="test_token",
        avatar_url="http://example.com/avatar.jpg",
    )


@pytest.fixture
def user_repository(mock_session: AsyncSession):
    return UserRepository(mock_session)


@pytest.mark.asyncio
async def test_get_by_email(
    mock_session: AsyncSession, test_user: User, user_repository: UserRepository
):
    # Setup mock
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute.return_value = mock_result

    # Execute
    result = await user_repository.get_by_email(test_user.email)

    # Verify
    assert result is test_user
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_email_not_found(
    mock_session: AsyncSession, user_repository: UserRepository
):
    # Setup mock
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    # Execute
    result = await user_repository.get_by_email("nonexistent@example.com")

    # Verify
    assert result is None
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_email_verification_token(
    mock_session: AsyncSession, test_user: User, user_repository: UserRepository
):
    # Setup mock
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute.return_value = mock_result

    # Execute
    result = await user_repository.get_by_email_verification_token(
        test_user.verification_token
    )

    # Verify
    assert result is test_user
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_email_verification_token_not_found(
    mock_session: AsyncSession, user_repository: UserRepository
):
    # Setup mock
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    # Execute
    result = await user_repository.get_by_email_verification_token("invalid_token")

    # Verify
    assert result is None
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_create(mock_session: AsyncSession, user_repository: UserRepository):
    # Setup test data
    user_data = {
        "username": "new_user",
        "email": "new@example.com",
        "password": "hashed_password",
        "verification_token": "new_token",
    }

    # Execute
    result = await user_repository.create(user_data)

    # Verify
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

    # Since we're not mocking the User creation, we need to verify the data differently
    assert isinstance(result, User)
    assert result.username == user_data["username"]
    assert result.email == user_data["email"]
    assert result.password == user_data["password"]
    assert result.verification_token == user_data["verification_token"]


@pytest.mark.asyncio
async def test_update(
    mock_session: AsyncSession, test_user: User, user_repository: UserRepository
):
    # Execute
    test_user.username = "updated_username"
    result = await user_repository.update(test_user)

    # Verify
    mock_session.commit.assert_called_once()
    assert result is test_user
    assert result.username == "updated_username"


@pytest.mark.asyncio
async def test_update_avatar(
    mock_session: AsyncSession, test_user: User, user_repository: UserRepository
):
    # Setup
    new_avatar_url = "http://example.com/new_avatar.jpg"

    # Execute
    result = await user_repository.update_avatar(test_user, new_avatar_url)

    # Verify
    assert result.avatar_url == new_avatar_url
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(test_user)
