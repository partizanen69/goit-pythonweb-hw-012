import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock
from fastapi import HTTPException
from typing import List

from src.services.contacts import ContactsService
from src.repository.contacts import ContactsRepository
from src.models.base import Contact, User
from src.schemas.contact import ContactCreate, ContactUpdate
from src.exceptions.contact import ContactAlreadyExists


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock(spec=ContactsRepository)


@pytest.fixture
def contacts_service(mock_repository: AsyncMock) -> ContactsService:
    service = ContactsService(AsyncMock())
    service.repository = mock_repository
    return service


@pytest.fixture
def test_user() -> User:
    return User(
        id=1, username="test_user", email="test@example.com", password="password"
    )


@pytest.fixture
def contact_data() -> ContactCreate:
    return ContactCreate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
        birthday=date(1990, 1, 1),
    )


@pytest.mark.asyncio
async def test_create_contact_success(
    contacts_service: ContactsService, contact_data: ContactCreate, test_user: User
) -> None:
    # Setup
    mock_contact = Contact(id=1, user_id=test_user.id, **contact_data.model_dump())
    contacts_service.repository.create_contact.return_value = mock_contact

    # Execute
    result = await contacts_service.create_contact(contact_data, test_user.id)

    # Verify
    contacts_service.repository.create_contact.assert_called_once_with(
        contact_data, test_user.id
    )
    assert result == mock_contact


@pytest.mark.asyncio
async def test_create_contact_duplicate_email(
    contacts_service: ContactsService, contact_data: ContactCreate, test_user: User
) -> None:
    # Setup
    error_message = f"Contact with email {contact_data.email} already exists"
    contacts_service.repository.create_contact.side_effect = ContactAlreadyExists(
        error_message
    )

    # Execute & Verify
    with pytest.raises(HTTPException) as exc_info:
        await contacts_service.create_contact(contact_data, test_user.id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == error_message
    contacts_service.repository.create_contact.assert_called_once_with(
        contact_data, test_user.id
    )


@pytest.mark.asyncio
async def test_get_contacts(contacts_service: ContactsService, test_user: User) -> None:
    # Setup
    expected_contacts: List[Contact] = [
        Contact(
            id=i + 1,
            first_name=f"User{i}",
            last_name=f"Test{i}",
            email=f"user{i}@test.com",
            phone=f"123456789{i}",
            birthday=date(1990, 1, 1),
            user_id=test_user.id,
        )
        for i in range(3)
    ]
    contacts_service.repository.get_contacts.return_value = expected_contacts

    # Execute
    result = await contacts_service.get_contacts(
        skip=0,
        limit=10,
        first_name="Test",
        last_name="User",
        email="test",
        user_id=test_user.id,
    )

    # Verify
    contacts_service.repository.get_contacts.assert_called_once_with(
        0, 10, "Test", "User", "test", test_user.id
    )
    assert result == expected_contacts


@pytest.mark.asyncio
async def test_get_upcoming_birthdays(
    contacts_service: ContactsService, test_user: User
) -> None:
    # Setup
    today = date.today()
    expected_contacts: List[Contact] = [
        Contact(
            id=1,
            first_name="Today",
            last_name="Birthday",
            email="today@example.com",
            phone="1234567890",
            birthday=today,
            user_id=test_user.id,
        ),
        Contact(
            id=2,
            first_name="Tomorrow",
            last_name="Birthday",
            email="tomorrow@example.com",
            phone="0987654321",
            birthday=today + timedelta(days=1),
            user_id=test_user.id,
        ),
    ]
    contacts_service.repository.get_upcoming_birthdays.return_value = expected_contacts

    # Execute
    result = await contacts_service.get_upcoming_birthdays(test_user.id)

    # Verify
    contacts_service.repository.get_upcoming_birthdays.assert_called_once()
    assert result == expected_contacts


@pytest.mark.asyncio
async def test_get_contact(contacts_service: ContactsService, test_user: User) -> None:
    # Setup
    contact_id: int = 1
    expected_contact = Contact(
        id=contact_id,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
        birthday=date(1990, 1, 1),
        user_id=test_user.id,
    )
    contacts_service.repository.get_contact.return_value = expected_contact

    # Execute
    result = await contacts_service.get_contact(contact_id, test_user.id)

    # Verify
    contacts_service.repository.get_contact.assert_called_once_with(
        contact_id, test_user.id
    )
    assert result == expected_contact


@pytest.mark.asyncio
async def test_update_contact(
    contacts_service: ContactsService, test_user: User
) -> None:
    # Setup
    contact_id: int = 1
    update_data = ContactUpdate(first_name="Jane", phone="9876543210")
    updated_contact = Contact(
        id=contact_id,
        first_name="Jane",  # Updated
        last_name="Doe",
        email="john@example.com",
        phone="9876543210",  # Updated
        birthday=date(1990, 1, 1),
        user_id=test_user.id,
    )
    contacts_service.repository.update_contact.return_value = updated_contact

    # Execute
    result = await contacts_service.update_contact(
        contact_id, update_data, test_user.id
    )

    # Verify
    contacts_service.repository.update_contact.assert_called_once_with(
        contact_id, update_data, test_user.id
    )
    assert result == updated_contact


@pytest.mark.asyncio
async def test_delete_contact(
    contacts_service: ContactsService, test_user: User
) -> None:
    # Setup
    contact_id: int = 1

    # Execute
    await contacts_service.delete_contact(contact_id, test_user.id)

    # Verify
    contacts_service.repository.delete_contact.assert_called_once_with(
        contact_id, test_user.id
    )
