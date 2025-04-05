from unittest.mock import AsyncMock
from datetime import UTC, datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from src.models.base import User
from tests.conftest import TestingSessionLocal

user_data = {
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
}


def test_register(client, monkeypatch):
    mock_send_email = AsyncMock()
    monkeypatch.setattr(
        "src.services.email.EmailService.send_verification_email", mock_send_email
    )
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar_url" in data
    mock_send_email.assert_called_once()
    email, username, token = mock_send_email.call_args[0]

    assert email == user_data["email"]
    assert username == user_data["username"]
    assert isinstance(token, str)


def test_repeat_register_email(client, monkeypatch):
    mock_send_email = AsyncMock()
    monkeypatch.setattr(
        "src.services.email.EmailService.send_verification_email", mock_send_email
    )
    user_copy = user_data.copy()
    user_copy["username"] = "kot_leapold"
    response = client.post("api/auth/register", json=user_copy)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Email already registered"


def test_not_confirmed_login(client):
    login_data = {
        "email": user_data.get("email"),
        "password": user_data.get("password"),
    }

    response = client.post("api/auth/login", json=login_data)
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not verified"


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.email_verified = True
            await session.commit()

    login_data = {
        "email": user_data.get("email"),
        "password": user_data.get("password"),
    }

    response = client.post("api/auth/login", json=login_data)

    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


def test_wrong_password_login(client):
    login_data = {
        "email": user_data.get("email"),
        "password": "password",
    }

    response = client.post("api/auth/login", json=login_data)
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Incorrect email or password"


def test_wrong_username_login(client):
    login_data = {
        "email": "username@gmail.com",
        "password": user_data.get("password"),
    }

    response = client.post("api/auth/login", json=login_data)
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Incorrect email or password"


def test_validation_error_login(client):
    login_data = {
        "email": user_data.get("email"),
    }

    response = client.post("api/auth/login", json=login_data)
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_request_password_reset(client, monkeypatch):
    # Mock email sending
    mock_send_email = AsyncMock()
    monkeypatch.setattr(
        "src.services.email.EmailService.send_password_reset_email", mock_send_email
    )

    # Request password reset for existing user
    request_data = {"email": user_data.get("email")}
    response = client.post("api/auth/request-password-reset", json=request_data)

    assert response.status_code == 200, response.text
    data = response.json()
    assert (
        data["message"]
        == "If your email is registered, you will receive a password reset link"
    )

    # Verify email was sent
    mock_send_email.assert_called_once()
    email, username, token = mock_send_email.call_args[0]
    assert email == user_data["email"]
    assert username == user_data["username"]
    assert isinstance(token, str)

    # Get the generated token from the database
    reset_token = None
    async with TestingSessionLocal() as session:
        db_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        db_user = db_user.scalar_one_or_none()
        reset_token = db_user.reset_password_token
        assert reset_token is not None
        assert db_user.reset_token_expires is not None
        assert db_user.reset_token_expires > datetime.now(timezone.utc).replace(
            tzinfo=None
        )

    return reset_token


@pytest.mark.asyncio
async def test_request_password_reset_nonexistent_user(client, monkeypatch):
    # Mock email sending
    mock_send_email = AsyncMock()
    monkeypatch.setattr(
        "src.services.email.EmailService.send_password_reset_email", mock_send_email
    )

    # Request password reset for non-existent user
    request_data = {"email": "nonexistent@example.com"}
    response = client.post("api/auth/request-password-reset", json=request_data)

    # Should still return 200 to prevent user enumeration
    assert response.status_code == 200, response.text
    data = response.json()
    assert (
        data["message"]
        == "If your email is registered, you will receive a password reset link"
    )

    # Verify no email was sent
    mock_send_email.assert_not_called()


@pytest.mark.asyncio
async def test_reset_password(client, monkeypatch):
    # First request password reset to get token
    reset_token = await test_request_password_reset(client, monkeypatch)

    # Reset password
    reset_data = {"token": reset_token, "password": "newpassword123"}
    response = client.post(f"api/auth/reset-password/{reset_token}", json=reset_data)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Password reset successfully"

    # Try to login with new password
    login_data = {
        "email": user_data.get("email"),
        "password": "newpassword123",
    }

    response = client.post("api/auth/login", json=login_data)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_reset_password_invalid_token(client):
    # Try to reset with invalid token
    reset_data = {"token": "invalid-token", "password": "newpassword123"}
    response = client.post("api/auth/reset-password/invalid-token", json=reset_data)

    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Invalid reset token"


@pytest.mark.asyncio
async def test_reset_password_expired_token(client, monkeypatch):
    # First request password reset
    reset_token = await test_request_password_reset(client, monkeypatch)

    # Expire the token manually
    async with TestingSessionLocal() as session:
        db_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        db_user = db_user.scalar_one_or_none()
        db_user.reset_token_expires = datetime.now(UTC) - timedelta(hours=1)
        await session.commit()

    # Try to reset with expired token
    reset_data = {"token": reset_token, "password": "newpassword123"}
    response = client.post(f"api/auth/reset-password/{reset_token}", json=reset_data)

    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Reset token has expired"
