from unittest.mock import AsyncMock
import pytest
import io
from fastapi.testclient import TestClient


def test_update_avatar_unauthorized(client: TestClient):
    """Test updating avatar without authentication."""
    response = client.patch(
        "api/users/avatar",
        files={
            "file": ("test_image.jpg", io.BytesIO(b"test image content"), "image/jpeg")
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Not authenticated"


def test_update_avatar_with_invalid_file_type(client: TestClient, get_token: str):
    """Test updating avatar with an invalid file type."""
    response = client.patch(
        "api/users/avatar",
        files={
            "file": ("test_file.txt", io.BytesIO(b"this is not an image"), "text/plain")
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "File must be an image"


def test_update_avatar_success(
    client: TestClient, get_token: str, monkeypatch: pytest.MonkeyPatch
):
    """Test successfully updating a user's avatar."""
    # Mock the CloudImage.upload method
    mock_cloud_upload = AsyncMock()
    mock_cloud_upload.return_value = {"secure_url": "https://example.com/avatar.jpg"}
    monkeypatch.setattr("src.services.cloud_image.CloudImage.upload", mock_cloud_upload)

    # Create a test image
    test_image_content = b"test image content"

    # Make the request
    response = client.patch(
        "api/users/avatar",
        files={
            "file": ("test_image.jpg", io.BytesIO(test_image_content), "image/jpeg")
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )

    # Assert response
    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data
    assert "username" in data
    assert "email" in data
    assert data["avatar_url"] == "https://example.com/avatar.jpg"

    # Verify the mock was called
    mock_cloud_upload.assert_called_once()

    # Verify the file content was passed to the mock
    file_content, kwargs = mock_cloud_upload.call_args
    assert kwargs["public_id"].startswith("ContactsApp/")
    assert file_content[0] == test_image_content
