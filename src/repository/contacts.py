from typing import List, Optional
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas.contacts import ContactModel


class ContactsRepository:
    def __init__(self, session: AsyncSession):
        """
        Initialize the ContactsRepository with a database session.

        Args:
            session (AsyncSession): The asynchronous database session to be used for database operations.
        """
        self.db = session
        self.db = session

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        """
        Create a new contact.

        Args:
            body (ContactModel): The contact to create.
            user (User): The user the contact belongs to.

        Returns:
            Contact: The created contact.
        """
        contact = Contact(**body.model_dump(exclude_unset=True), user_id=user.id)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def read_contacts(
        self,
        user: User,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        email: Optional[str] = None,
        upcoming_birthday_days: Optional[int] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[Contact]:
        """
        Read contacts from the database.

        Args:
            user (User): The user the contacts belong to.
            firstname (Optional[str]): The firstname to search for. Defaults to None.
            lastname (Optional[str]): The lastname to search for. Defaults to None.
            email (Optional[str]): The email to search for. Defaults to None.
            upcoming_birthday_days (Optional[int]): The number of days to search for contacts with upcoming birthdays. Defaults to None.
            skip (int): The number of contacts to skip. Defaults to 0.
            limit (int): The maximum number of contacts to return. Defaults to 10.

        Returns:
            List[Contact]: The list of contacts.
        """
        stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)

        if firstname:
            stmt = stmt.where(Contact.firstname.match(firstname))
        if lastname:
            stmt = stmt.where(Contact.lastname.match(lastname))
        if email:
            stmt = stmt.where(Contact.email.match(email))

        if upcoming_birthday_days:
            stmt = stmt.where(
                Contact.birthday.between(
                    date.today(), date.today() + timedelta(days=upcoming_birthday_days)
                )
            )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def read_contact(self, contact_id: int, user: User) -> Optional[Contact]:
        """
        Read a contact from the database.

        Args:
            contact_id (int): The ID of the contact to read.
            user (User): The user the contact belongs to.

        Returns:
            Optional[Contact]: The contact if it exists, otherwise None.
        """
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_contact(
        self, contact_id: int, body: ContactModel, user: User
    ) -> Optional[Contact]:
        """
        Update a contact in the database.

        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactModel): The contact data to update.
            user (User): The user the contact belongs to.

        Returns:
            Optional[Contact]: The updated contact if it exists, otherwise None.
        """
        contact = await self.read_contact(contact_id, user)
        if contact:
            for key, value in body.model_dump(exclude_unset=True).items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def delete_contact(self, contact_id: int, user: User) -> Optional[Contact]:
        """
        Delete a contact from the database.

        Args:
            contact_id (int): The ID of the contact to delete.
            user (User): The user the contact belongs to.

        Returns:
            Optional[Contact]: The deleted contact if it exists, otherwise None.
        """
        contact = await self.read_contact(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact
