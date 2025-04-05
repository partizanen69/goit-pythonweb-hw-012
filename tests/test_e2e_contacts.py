from datetime import date, timedelta
from typing import Dict, Any
from fastapi.testclient import TestClient

contact_data: Dict[str, str] = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "1234567890",
    "birthday": str(date.today() - timedelta(days=365 * 30)),
    "additional_data": "Test contact",
}

updated_contact_data: Dict[str, str] = {
    "first_name": "Jane",
    "last_name": "Smith",
    "phone": "9876543210",
}


def test_create_contact_unauthorized(client: TestClient) -> None:
    response = client.post("api/contacts/", json=contact_data)
    assert response.status_code == 401, response.text


def test_create_contact(client: TestClient, get_token: str) -> int:
    response = client.post(
        "api/contacts/",
        json=contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["first_name"] == contact_data["first_name"]
    assert data["last_name"] == contact_data["last_name"]
    assert data["email"] == contact_data["email"]
    assert data["phone"] == contact_data["phone"]
    assert "id" in data
    return data["id"]


def test_get_contact(client: TestClient, get_token: str) -> None:
    # First create a contact
    new_contact_data = contact_data.copy()
    new_contact_data["email"] = "another_email@example.com"
    response = client.post(
        "api/contacts/",
        json=new_contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text

    created_contact = response.json()

    # Get the contact by ID
    response = client.get(
        f"api/contacts/{created_contact['id']}",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == created_contact["id"]
    assert data["first_name"] == new_contact_data["first_name"]
    assert data["last_name"] == new_contact_data["last_name"]
    assert data["email"] == new_contact_data["email"]


def test_get_contacts(client: TestClient, get_token: str) -> None:
    response = client.get(
        "api/contacts/", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_contacts_with_filtering(client: TestClient, get_token: str) -> None:
    response = client.get(
        f"api/contacts/?first_name={contact_data['first_name']}",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert all(contact["first_name"] == contact_data["first_name"] for contact in data)


def test_get_contacts_pagination(client: TestClient, get_token: str) -> None:
    # Add multiple contacts for pagination testing
    for i in range(3):
        new_contact = contact_data.copy()
        new_contact["email"] = f"test{i}@example.com"
        new_contact["phone"] = f"12345{i}7890"
        response = client.post(
            "api/contacts/",
            json=new_contact,
            headers={"Authorization": f"Bearer {get_token}"},
        )
        assert response.status_code == 201, response.text

    # Test limit parameter
    response = client.get(
        "api/contacts/?limit=2", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) <= 2


def test_update_contact(client: TestClient, get_token: str) -> None:
    # First create a contact
    new_contact_data = contact_data.copy()
    new_contact_data["email"] = "another_email2@example.com"
    response = client.post(
        "api/contacts/",
        json=new_contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    created_contact = response.json()

    # Update the contact
    response = client.put(
        f"api/contacts/{created_contact['id']}",
        json=updated_contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == created_contact["id"]
    assert data["first_name"] == updated_contact_data["first_name"]
    assert data["last_name"] == updated_contact_data["last_name"]
    assert data["phone"] == updated_contact_data["phone"]

    # Fields that weren't updated should remain the same
    assert data["email"] == new_contact_data["email"]


def test_update_nonexistent_contact(client: TestClient, get_token: str) -> None:
    response = client.put(
        "api/contacts/9999",
        json=updated_contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert "not found" in data["detail"]


def test_delete_contact(client: Any, get_token: str) -> None:
    # First create a contact
    new_contact_data = contact_data.copy()
    new_contact_data["email"] = "another_email3@example.com"
    response = client.post(
        "api/contacts/",
        json=new_contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    created_contact = response.json()

    # Delete the contact
    response = client.delete(
        f"api/contacts/{created_contact['id']}",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 204, response.text

    # Verify the contact was deleted
    response = client.get(
        f"api/contacts/{created_contact['id']}",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text


def test_delete_nonexistent_contact(client: TestClient, get_token: str) -> None:
    response = client.delete(
        "api/contacts/9999", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert "not found" in data["detail"]


def test_get_upcoming_birthdays(client: TestClient, get_token: str) -> None:
    # Create a contact with an upcoming birthday (within next 7 days)
    upcoming_birthday = date.today() + timedelta(days=3)
    birthday_contact = contact_data.copy()
    birthday_contact["email"] = "upcoming@example.com"
    birthday_contact["phone"] = "5555555555"
    birthday_contact["birthday"] = str(
        upcoming_birthday.replace(year=upcoming_birthday.year - 30)
    )

    response = client.post(
        "api/contacts/",
        json=birthday_contact,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text

    # Test upcoming birthdays endpoint
    response = client.get(
        "api/contacts/birthdays", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)

    # Check if our contact with an upcoming birthday is in the response
    emails = [contact["email"] for contact in data]
    assert "upcoming@example.com" in emails
