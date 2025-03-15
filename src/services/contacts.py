from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.repository.contacts import ContactsRepository
from src.schemas.contact import ContactCreate, ContactResponse, ContactUpdate


class ContactsService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactsRepository(db)

    async def create_contact(self, contact: ContactCreate) -> ContactResponse:
        return await self.repository.create_contact(contact)

    async def get_contacts(
        self,
        skip: int,
        limit: int,
        first_name: Optional[str],
        last_name: Optional[str],
        email: Optional[str],
    ) -> List[ContactResponse]:
        return await self.repository.get_contacts(
            skip, limit, first_name, last_name, email
        )

    async def get_upcoming_birthdays(self) -> List[ContactResponse]:
        return await self.repository.get_upcoming_birthdays()

    async def get_contact(self, contact_id: int) -> ContactResponse:
        return await self.repository.get_contact(contact_id)

    async def update_contact(
        self, contact_id: int, contact: ContactUpdate
    ) -> ContactResponse:
        return await self.repository.update_contact(contact_id, contact)

    async def delete_contact(self, contact_id: int) -> None:
        await self.repository.delete_contact(contact_id)
