"""Contact management routes for the Contacts API.

This module provides endpoints for creating, reading, updating, and deleting contacts,
as well as retrieving upcoming birthdays.
"""

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
    """Create a new contact.

    Args:
        contact (ContactCreate): Contact data to create
        db (AsyncSession): Database session
        current_user (User): Current authenticated user

    Returns:
        ContactResponse: Created contact data
    """
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
    """Get a list of contacts with optional filtering.

    Args:
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        first_name (Optional[str]): Filter by first name
        last_name (Optional[str]): Filter by last name
        email (Optional[str]): Filter by email
        db (AsyncSession): Database session
        current_user (User): Current authenticated user

    Returns:
        List[ContactResponse]: List of contacts matching the criteria
    """
    service = ContactsService(db)
    return await service.get_contacts(skip, limit, first_name, last_name, email, current_user.id)


@router.get("/birthdays", response_model=List[ContactResponse])
async def get_upcoming_birthdays(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
) -> List[ContactResponse]:
    """Get a list of contacts with upcoming birthdays.

    Args:
        db (AsyncSession): Database session
        current_user (User): Current authenticated user

    Returns:
        List[ContactResponse]: List of contacts with upcoming birthdays
    """
    service = ContactsService(db)
    return await service.get_upcoming_birthdays(current_user.id)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
) -> ContactResponse:
    """Get a specific contact by ID.

    Args:
        contact_id (int): ID of the contact to retrieve
        db (AsyncSession): Database session
        current_user (User): Current authenticated user

    Returns:
        ContactResponse: Contact data

    Raises:
        HTTPException: If contact is not found
    """
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
    """Update a specific contact.

    Args:
        contact_id (int): ID of the contact to update
        contact (ContactUpdate): Updated contact data
        db (AsyncSession): Database session
        current_user (User): Current authenticated user

    Returns:
        ContactResponse: Updated contact data

    Raises:
        HTTPException: If contact is not found
    """
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
    """Delete a specific contact.

    Args:
        contact_id (int): ID of the contact to delete
        db (AsyncSession): Database session
        current_user (User): Current authenticated user

    Raises:
        HTTPException: If contact is not found
    """
    service = ContactsService(db)
    contact = await service.get_contact(contact_id, current_user.id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found",
        )
    await service.delete_contact(contact_id, current_user.id)
