from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from src.database.db import get_db
from src.services.contacts import ContactsService
from src.schemas.contact import ContactCreate, ContactResponse, ContactUpdate
from src.services.auth import AuthService
from src.models.base import User

router = APIRouter(prefix="/contacts", tags=["contacts"], dependencies=[Depends(AuthService.get_current_user)])
logger = logging.getLogger("uvicorn.error")


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
) -> ContactResponse:
    service = ContactsService(db)
    return await service.create_contact(contact, current_user.id)


@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    first_name: Optional[str] = Query(default=None),
    last_name: Optional[str] = Query(default=None),
    email: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
) -> List[ContactResponse]:
    service = ContactsService(db)
    return await service.get_contacts(skip, limit, first_name, last_name, email, current_user.id)


@router.get("/birthdays", response_model=List[ContactResponse])
async def get_upcoming_birthdays(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
) -> List[ContactResponse]:
    service = ContactsService(db)
    return await service.get_upcoming_birthdays(current_user.id)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
) -> ContactResponse:
    service = ContactsService(db)
    contact = await service.get_contact(contact_id, current_user.id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found",
        )
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
) -> ContactResponse:
    service = ContactsService(db)
    existing_contact = await service.get_contact(contact_id, current_user.id)
    if existing_contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found",
        )
    return await service.update_contact(contact_id, contact, current_user.id)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
) -> None:
    service = ContactsService(db)
    contact = await service.get_contact(contact_id, current_user.id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found",
        )
    await service.delete_contact(contact_id, current_user.id)
