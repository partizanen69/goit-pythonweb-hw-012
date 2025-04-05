import pytest
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, Mock
from src.models.base import Contact, User
from src.schemas.contact import ContactCreate, ContactUpdate
from src.repository.contacts import ContactsRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.exceptions.contact import ContactAlreadyExists


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
        id=1, username="test_user", email="test@example.com", password="password"
    )


@pytest.fixture
def contact_data():
    return ContactCreate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
        birthday=date(1990, 1, 1),
    )


@pytest.fixture
def contacts_repository(mock_session: AsyncSession):
    return ContactsRepository(mock_session)


@pytest.mark.asyncio
async def test_create_contact_success(
    mock_session: AsyncSession,
    test_user: User,
    contact_data: ContactCreate,
    contacts_repository: ContactsRepository,
):
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    mock_created_contact = Contact(
        id=1, user_id=test_user.id, **contact_data.model_dump()
    )
    mock_session.refresh.return_value = mock_created_contact

    result = await contacts_repository.create_contact(contact_data, test_user.id)

    # Verify
    assert result.user_id == test_user.id
    assert result.first_name == contact_data.first_name
    assert result.last_name == contact_data.last_name
    assert result.email == contact_data.email
    assert result.phone == contact_data.phone
    assert result.birthday == contact_data.birthday

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_create_contact_duplicate_email(
    mock_session: AsyncSession,
    test_user: User,
    contact_data: ContactCreate,
    contacts_repository: ContactsRepository,
):
    mock_existing_contact = Mock()
    mock_session.execute.return_value = mock_existing_contact
    mock_existing_contact.scalar_one_or_none.return_value = Contact(
        id=1, user_id=test_user.id, **contact_data.model_dump()
    )

    # Execute & Verify
    with pytest.raises(ContactAlreadyExists) as exc_info:
        await contacts_repository.create_contact(contact_data, test_user.id)

    assert (
        str(exc_info.value) == f"Contact with email {contact_data.email} already exists"
    )
    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_get_contacts(
    mock_session: AsyncSession,
    test_user: User,
    contacts_repository: ContactsRepository,
):
    # Create test contacts
    expected_contacts = [
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

    # Setup proper mock chain
    mock_scalars = MagicMock()
    mock_all = MagicMock(return_value=expected_contacts)
    mock_scalars.all = mock_all

    mock_result = AsyncMock()
    mock_result.scalars = MagicMock(return_value=mock_scalars)

    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call get_contacts
    result = await contacts_repository.get_contacts(
        skip=0,
        limit=10,
        first_name=None,
        last_name=None,
        email=None,
        user_id=test_user.id,
    )

    # Verify query building
    mock_session.execute.assert_called_once()

    # Assertions on result
    assert len(result) == 3
    for i, contact in enumerate(result):
        assert contact.id == i + 1
        assert contact.first_name == f"User{i}"
        assert contact.last_name == f"Test{i}"
        assert contact.email == f"user{i}@test.com"
        assert contact.phone == f"123456789{i}"
        assert contact.birthday == date(1990, 1, 1)
        assert contact.user_id == test_user.id


@pytest.mark.asyncio
async def test_get_contact(
    mock_session: AsyncSession, test_user: User, contacts_repository: ContactsRepository
):
    # Setup test data
    contact_id = 1
    expected_contact = Contact(
        id=contact_id,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
        birthday=date(1990, 1, 1),
        user_id=test_user.id,
    )

    # Mock session.execute result
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = expected_contact
    mock_session.execute.return_value = mock_result

    # Execute get_contact
    result = await contacts_repository.get_contact(contact_id, test_user.id)

    # Verify
    assert result is expected_contact
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_contact_not_found(
    mock_session: AsyncSession, test_user: User, contacts_repository: ContactsRepository
):
    # Setup
    contact_id = 999  # Non-existent ID

    # Mock session.execute result for not found
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    # Execute get_contact
    result = await contacts_repository.get_contact(contact_id, test_user.id)

    # Verify
    assert result is None
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_update_contact(
    mock_session: AsyncSession, test_user: User, contacts_repository: ContactsRepository
):
    # Setup test data
    contact_id = 1
    existing_contact = Contact(
        id=contact_id,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
        birthday=date(1990, 1, 1),
        user_id=test_user.id,
    )

    # Mock get_contact to return existing contact
    contacts_repository.get_contact = AsyncMock(return_value=existing_contact)

    # Create update data
    update_data = ContactUpdate(first_name="Jane", phone="9876543210")

    # Execute update_contact
    result = await contacts_repository.update_contact(
        contact_id, update_data, test_user.id
    )

    # Verify
    contacts_repository.get_contact.assert_called_once_with(contact_id, test_user.id)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(existing_contact)

    # Check updated fields
    assert result.first_name == "Jane"  # Updated
    assert result.last_name == "Doe"  # Unchanged
    assert result.email == "john@example.com"  # Unchanged
    assert result.phone == "9876543210"  # Updated
    assert result.birthday == date(1990, 1, 1)  # Unchanged
    assert result.user_id == test_user.id  # Unchanged


@pytest.mark.asyncio
async def test_delete_contact(
    mock_session: AsyncSession, test_user: User, contacts_repository: ContactsRepository
):
    # Setup test data
    contact_id = 1
    existing_contact = Contact(
        id=contact_id,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
        birthday=date(1990, 1, 1),
        user_id=test_user.id,
    )

    # Mock get_contact to return existing contact
    contacts_repository.get_contact = AsyncMock(return_value=existing_contact)
    mock_session.delete = AsyncMock()

    # Execute delete_contact
    await contacts_repository.delete_contact(contact_id, test_user.id)

    # Verify
    contacts_repository.get_contact.assert_called_once_with(contact_id, test_user.id)
    mock_session.delete.assert_called_once_with(existing_contact)
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_get_upcoming_birthdays(
    mock_session: AsyncSession, test_user: User, contacts_repository: ContactsRepository
):
    # Create test contacts with upcoming birthdays
    today = datetime.now().date()

    expected_contacts = [
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
        Contact(
            id=3,
            first_name="NextWeek",
            last_name="Birthday",
            email="nextweek@example.com",
            phone="5555555555",
            birthday=today + timedelta(days=7),
            user_id=test_user.id,
        ),
    ]

    # Setup mock chain
    mock_scalars = MagicMock()
    mock_all = MagicMock(return_value=expected_contacts)
    mock_scalars.all = mock_all

    mock_result = AsyncMock()
    mock_result.scalars = MagicMock(return_value=mock_scalars)

    mock_session.execute = AsyncMock(return_value=mock_result)

    # Execute get_upcoming_birthdays
    result = await contacts_repository.get_upcoming_birthdays()

    # Verify
    mock_session.execute.assert_called_once()

    # Assertions on result
    assert len(result) == 3
    assert result[0].first_name == "Today"
    assert result[1].first_name == "Tomorrow"
    assert result[2].first_name == "NextWeek"

    # Check birthdays are within the expected range (today to today+7)
    for contact in result:
        assert contact.birthday >= today
        assert contact.birthday <= today + timedelta(days=7)
