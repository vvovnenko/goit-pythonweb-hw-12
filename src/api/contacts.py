from typing import List, Optional

from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas.contacts import ContactModel, ContactResponseModel
from src.service.auth import get_current_user
from src.service.contacts import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post(
    "/",
    response_model=ContactResponseModel,
    status_code=status.HTTP_201_CREATED,
    summary="Create new contact",
)
async def create_contact(
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ContactResponseModel:
    """
    Create a new contact for the authenticated user.

    Args:
        body (ContactModel): The contact details to create.
        db (AsyncSession): The database session dependency.
        user (User): The currently authenticated user.

    Returns:
        ContactResponseModel: The newly created contact.
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.get("/", response_model=List[ContactResponseModel], summary="Read contacts")
async def read_contacts(
    firstname: Optional[str] = Query(default=None, max_length=50, min_length=2),
    lastname: Optional[str] = Query(default=None, max_length=50, min_length=2),
    email: Optional[str] = Query(default=None, max_length=150, min_length=5),
    upcoming_birthday_days: Optional[int] = Query(
        default=None,
        ge=1,
        description="Пошук контактів з днями народження на найближчі upcoming_birthday_days днів",
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=5, le=100, ge=5),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> List[ContactResponseModel]:
    """
    Retrieve a list of contacts for the authenticated user, optionally filtered by firstname, lastname, email, and/or upcoming birthday.

    Args:
        firstname (Optional[str]): Filter contacts by their firstname.
        lastname (Optional[str]): Filter contacts by their lastname.
        email (Optional[str]): Filter contacts by their email.
        upcoming_birthday_days (Optional[int]): Filter contacts who have birthdays within these many upcoming days.
        skip (int): The number of records to skip for pagination.
        limit (int): The maximum number of records to return.
        db (AsyncSession): The database session dependency.
        user (User): The currently authenticated user.

    Returns:
        List[ContactResponseModel]: A list of contacts that match the query parameters.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.read_contacts(
        user, firstname, lastname, email, upcoming_birthday_days, skip, limit
    )
    return contacts


@router.get(
    "/{contact_id}", response_model=ContactResponseModel, summary="Read contact"
)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ContactResponseModel:
    """
    Retrieve a single contact by its ID for the authenticated user.

    Args:
        contact_id (int): The ID of the contact to retrieve.
        db (AsyncSession): The database session dependency.
        user (User): The currently authenticated user.

    Raises:
        HTTPException: If the contact is not found.

    Returns:
        ContactResponseModel: The requested contact details.
    """
    contact_service = ContactService(db)
    contact = await contact_service.read_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found."
        )
    return contact


@router.put(
    "/{contact_id}", response_model=ContactResponseModel, summary="Update contact"
)
async def update_contact(
    body: ContactModel,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ContactResponseModel:
    """
    Update an existing contact's details for the authenticated user.

    Args:
        body (ContactModel): The updated contact details.
        contact_id (int): The ID of the contact to update.
        db (AsyncSession): The database session dependency.
        user (User): The currently authenticated user.

    Raises:
        HTTPException: If the contact is not found.

    Returns:
        ContactResponseModel: The updated contact.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found."
        )
    return contact


@router.delete(
    "/{contact_id}", response_model=ContactResponseModel, summary="Delete contact"
)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ContactResponseModel:
    """
    Delete a contact by its ID for the authenticated user.

    Args:
        contact_id (int): The ID of the contact to delete.
        db (AsyncSession): The database session dependency.
        user (User): The currently authenticated user.

    Raises:
        HTTPException: If the contact is not found.

    Returns:
        ContactResponseModel: The deleted contact's details.
    """
    contact_service = ContactService(db)
    contact = await contact_service.delete_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found."
        )
    return contact
