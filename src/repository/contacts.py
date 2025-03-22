from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, extract, func
from sqlalchemy.future import select
from typing import List, Optional
from datetime import timedelta

from src.models.base import Contact
from src.schemas.contact import ContactCreate, ContactUpdate
from src.exceptions.contact import ContactAlreadyExists


class ContactsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_contact(self, contact: ContactCreate, user_id: int) -> Contact:
        existing_contact = await self.db.execute(
            select(Contact).where(
                and_(Contact.email == contact.email, Contact.user_id == user_id)
            )
        )
        if existing_contact.scalar_one_or_none():
            raise ContactAlreadyExists(
                f"Contact with email {contact.email} already exists"
            )

        db_contact = Contact(**contact.model_dump(), user_id=user_id)
        self.db.add(db_contact)
        await self.db.commit()
        await self.db.refresh(db_contact)
        return db_contact

    async def get_contacts(
        self,
        skip: int,
        limit: int,
        first_name: Optional[str],
        last_name: Optional[str],
        email: Optional[str],
        user_id: int,
    ) -> List[Contact]:
        query = select(Contact).where(Contact.user_id == user_id)

        # Apply filters if provided
        if first_name or last_name or email:
            filters = []
            if first_name:
                filters.append(Contact.first_name.ilike(f"%{first_name}%"))
            if last_name:
                filters.append(Contact.last_name.ilike(f"%{last_name}%"))
            if email:
                filters.append(Contact.email.ilike(f"%{email}%"))

            query = query.where(and_(or_(*filters), Contact.user_id == user_id))

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_contact(self, contact_id: int) -> Optional[Contact]:
        result = await self.db.execute(select(Contact).filter(Contact.id == contact_id))
        return result.scalar_one_or_none()

    async def update_contact(self, contact_id: int, contact: ContactUpdate) -> Contact:
        db_contact = await self.get_contact(contact_id)

        # Update only the provided fields
        update_data = contact.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_contact, key, value)

        await self.db.commit()
        await self.db.refresh(db_contact)
        return db_contact

    async def delete_contact(self, contact_id: int) -> None:
        db_contact = await self.get_contact(contact_id)
        await self.db.delete(db_contact)
        await self.db.commit()

    async def get_upcoming_birthdays(self) -> List[Contact]:
        query = select(Contact).where(
            and_(
                Contact.birthday >= func.current_date(),
                Contact.birthday <= func.current_date() + timedelta(days=7),
            )
        )

        result = await self.db.execute(query)
        return result.scalars().all()
