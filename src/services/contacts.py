"""Contact management service for the Contacts API.

This module provides business logic for managing contacts, including CRUD operations
and special queries like upcoming birthdays.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from fastapi import HTTPException, status

from src.repository.contacts import ContactsRepository
from src.schemas.contact import ContactCreate, ContactResponse, ContactUpdate
from src.exceptions.contact import ContactAlreadyExists


class ContactsService:
    """Service for managing contacts.

    This class provides methods for creating, reading, updating, and deleting contacts,
    as well as special queries like filtering contacts and getting upcoming birthdays.
    """

    def __init__(self, db: AsyncSession):
        """Initialize the contacts service.

        Args:
            db (AsyncSession): Database session
        """
        self.repository = ContactsRepository(db)

    async def create_contact(
        self, contact: ContactCreate, user_id: int
    ) -> ContactResponse:
        """Create a new contact.

        Args:
            contact (ContactCreate): Contact data to create
            user_id (int): ID of the user creating the contact

        Returns:
            ContactResponse: Created contact data

        Raises:
            HTTPException: If contact with this email already exists
        """
        try:
            return await self.repository.create_contact(contact, user_id)
        except ContactAlreadyExists as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def get_contacts(
        self,
        skip: int,
        limit: int,
        first_name: Optional[str],
        last_name: Optional[str],
        email: Optional[str],
        user_id: int,
    ) -> List[ContactResponse]:
        """Get a list of contacts with optional filtering.

        Args:
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            first_name (Optional[str]): Filter by first name
            last_name (Optional[str]): Filter by last name
            email (Optional[str]): Filter by email
            user_id (int): ID of the user whose contacts to retrieve

        Returns:
            List[ContactResponse]: List of contacts matching the criteria
        """
        return await self.repository.get_contacts(
            skip, limit, first_name, last_name, email, user_id
        )

    async def get_upcoming_birthdays(self, user_id: int) -> List[ContactResponse]:
        """Get a list of contacts with upcoming birthdays.

        Args:
            user_id (int): ID of the user whose contacts to check

        Returns:
            List[ContactResponse]: List of contacts with upcoming birthdays
        """
        return await self.repository.get_upcoming_birthdays()

    async def get_contact(self, contact_id: int, user_id: int) -> ContactResponse:
        """Get a specific contact by ID.

        Args:
            contact_id (int): ID of the contact to retrieve
            user_id (int): ID of the user who owns the contact

        Returns:
            ContactResponse: Contact data
        """
        return await self.repository.get_contact(contact_id, user_id)

    async def update_contact(
        self, contact_id: int, contact: ContactUpdate, user_id: int
    ) -> ContactResponse:
        """Update a specific contact.

        Args:
            contact_id (int): ID of the contact to update
            contact (ContactUpdate): Updated contact data
            user_id (int): ID of the user who owns the contact

        Returns:
            ContactResponse: Updated contact data
        """
        return await self.repository.update_contact(contact_id, contact, user_id)

    async def delete_contact(self, contact_id: int, user_id: int) -> None:
        """Delete a specific contact.

        Args:
            contact_id (int): ID of the contact to delete
            user_id (int): ID of the user who owns the contact
        """
        await self.repository.delete_contact(contact_id, user_id)
