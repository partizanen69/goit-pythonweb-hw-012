from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from fastapi import HTTPException, status

from src.repository.contacts import ContactsRepository
from src.schemas.contact import ContactCreate, ContactResponse, ContactUpdate
from src.exceptions.contact import ContactAlreadyExists


class ContactsService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactsRepository(db)

    async def create_contact(self, contact: ContactCreate, user_id: int) -> ContactResponse:
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
        return await self.repository.get_contacts(
            skip, limit, first_name, last_name, email, user_id
        )

    async def get_upcoming_birthdays(self, user_id: int) -> List[ContactResponse]:
        return await self.repository.get_upcoming_birthdays(user_id)

    async def get_contact(self, contact_id: int, user_id: int) -> ContactResponse:
        return await self.repository.get_contact(contact_id, user_id)

    async def update_contact(
        self, contact_id: int, contact: ContactUpdate, user_id: int
    ) -> ContactResponse:
        return await self.repository.update_contact(contact_id, contact, user_id)

    async def delete_contact(self, contact_id: int, user_id: int) -> None:
        await self.repository.delete_contact(contact_id, user_id)
