import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import UploadFile, HTTPException

from src.services.user import UserService
from src.repository.user_repository import UserRepository
from src.models.base import User
from src.services.cloud_image import CloudImage


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def user_service(mock_repository: AsyncMock) -> UserService:
    service = UserService(AsyncMock())
    service.repository = mock_repository
    return service


@pytest.fixture
def test_user() -> User:
    return User(
        id=1,
        username="test_user",
        email="test@example.com",
        password="hashed_password",
        avatar_url="http://example.com/old_avatar.jpg",
    )


@pytest.fixture
def mock_image_file() -> MagicMock:
    file = MagicMock(spec=UploadFile)
    file.filename = "avatar.jpg"
    file.content_type = "image/jpeg"
    file.read = AsyncMock(return_value=b"fake image content")
    return file


@pytest.mark.asyncio
async def test_update_avatar_success(
    user_service: UserService, test_user: User, mock_image_file: MagicMock
) -> None:
    # Setup
    new_avatar_url: str = "http://example.com/new_avatar.jpg"

    # Mock CloudImage.upload
    with patch.object(
        CloudImage, "upload", new=AsyncMock(return_value={"secure_url": new_avatar_url})
    ):
        # Mock repository update_avatar
        updated_user: User = User(
            id=test_user.id,
            username=test_user.username,
            email=test_user.email,
            password=test_user.password,
            avatar_url=new_avatar_url,  # Updated avatar URL
        )
        user_service.repository.update_avatar.return_value = updated_user

        # Execute
        result: User = await user_service.update_avatar(test_user, mock_image_file)

        # Verify
        mock_image_file.read.assert_called_once()
        user_service.repository.update_avatar.assert_called_once_with(
            test_user, new_avatar_url
        )
        assert result == updated_user
        assert result.avatar_url == new_avatar_url


@pytest.mark.asyncio
async def test_update_avatar_invalid_file_type(
    user_service: UserService, test_user: User
) -> None:
    # Setup
    invalid_file: MagicMock = MagicMock(spec=UploadFile)
    invalid_file.filename = "document.pdf"
    invalid_file.content_type = "application/pdf"

    # Execute & Verify
    with pytest.raises(HTTPException) as exc_info:
        await user_service.update_avatar(test_user, invalid_file)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "File must be an image"
    invalid_file.read.assert_not_called()
    user_service.repository.update_avatar.assert_not_called()


@pytest.mark.asyncio
async def test_update_avatar_missing_content_type(
    user_service: UserService, test_user: User
) -> None:
    # Setup
    invalid_file: MagicMock = MagicMock(spec=UploadFile)
    invalid_file.filename = "unknown"
    invalid_file.content_type = None  # Missing content type

    # Execute & Verify
    with pytest.raises(HTTPException) as exc_info:
        await user_service.update_avatar(test_user, invalid_file)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "File must be an image"
    invalid_file.read.assert_not_called()
    user_service.repository.update_avatar.assert_not_called()
