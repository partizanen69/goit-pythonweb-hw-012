from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, extract, func
from sqlalchemy.future import select
from typing import List, Optional
from datetime import datetime, timedelta

from src.models.contact import Contact
from src.schemas.contact import ContactCreate, ContactUpdate


class ContactsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_contact(self, contact: ContactCreate) -> Contact:
        db_contact = Contact(**contact.model_dump())
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
    ) -> List[Contact]:
        query = select(Contact)

        # Apply filters if provided
        if first_name or last_name or email:
            filters = []
            if first_name:
                filters.append(Contact.first_name.ilike(f"%{first_name}%"))
            if last_name:
                filters.append(Contact.last_name.ilike(f"%{last_name}%"))
            if email:
                filters.append(Contact.email.ilike(f"%{email}%"))

            query = query.where(or_(*filters))

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
        today = datetime.now().date()
        next_week = today + timedelta(days=7)

        # Handle year boundary case (December -> January)
        if today.month == 12 and next_week.month == 1:
            # Query for December birthdays
            december_query = select(Contact).where(
                and_(
                    extract("month", Contact.birthday) == 12,
                    extract("day", Contact.birthday) >= today.day,
                )
            )

            # Query for January birthdays
            january_query = select(Contact).where(
                and_(
                    extract("month", Contact.birthday) == 1,
                    extract("day", Contact.birthday) <= next_week.day,
                )
            )

            december_result = await self.db.execute(december_query)
            january_result = await self.db.execute(january_query)

            return december_result.scalars().all() + january_result.scalars().all()
        else:
            # Standard case within the same month
            if today.month == next_week.month:
                query = select(Contact).where(
                    and_(
                        extract("month", Contact.birthday) == today.month,
                        extract("day", Contact.birthday) >= today.day,
                        extract("day", Contact.birthday) <= next_week.day,
                    )
                )
            else:
                # Case when dates span two different months
                query = select(Contact).where(
                    or_(
                        and_(
                            extract("month", Contact.birthday) == today.month,
                            extract("day", Contact.birthday) >= today.day,
                        ),
                        and_(
                            extract("month", Contact.birthday) == next_week.month,
                            extract("day", Contact.birthday) <= next_week.day,
                        ),
                    )
                )

            result = await self.db.execute(query)
            return result.scalars().all()
