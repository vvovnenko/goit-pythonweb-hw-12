from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactsRepository
from src.schemas.contacts import ContactModel


class ContactService:
    def __init__(self, db_session: AsyncSession):
        """
        Initializes the ContactService with a given asynchronous database session.

        Args:
            db_session (AsyncSession): The asynchronous SQLAlchemy session to interact with the database.
        """
        self.repository = ContactsRepository(db_session)

    async def create_contact(self, contact_data: ContactModel, user: User) -> Contact:
        """
        Creates a new contact associated with the specified user.

        Args:
            contact_data (ContactModel): The data of the contact to create.
            user (User): The user creating the contact.

        Returns:
            Contact: The newly created contact instance.
        """
        return await self.repository.create_contact(contact_data, user)

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
        Retrieves a list of contacts for the given user, optionally filtered by firstname, lastname, email, or upcoming birthdays.
        Supports pagination through skip and limit parameters.

        Args:
            user (User): The owner of the contacts.
            firstname (Optional[str]): Filter by the contact's first name. Defaults to None.
            lastname (Optional[str]): Filter by the contact's last name. Defaults to None.
            email (Optional[str]): Filter by the contact's email. Defaults to None.
            upcoming_birthday_days (Optional[int]): Filter by contacts whose birthday falls within the next given days. Defaults to None.
            skip (int): Number of records to skip. Defaults to 0.
            limit (int): Maximum number of records to return. Defaults to 10.

        Returns:
            List[Contact]: A list of contact instances matching the criteria.
        """
        return await self.repository.read_contacts(
            user, firstname, lastname, email, upcoming_birthday_days, skip, limit
        )

    async def read_contact(self, contact_id: int, user: User) -> Optional[Contact]:
        """
        Retrieves a single contact by its ID, ensuring it belongs to the specified user.

        Args:
            contact_id (int): The ID of the contact to retrieve.
            user (User): The owner of the contact.

        Returns:
            Optional[Contact]: The contact if found and owned by the user, otherwise None.
        """
        return await self.repository.read_contact(contact_id, user)

    async def update_contact(
        self, contact_id: int, contact_data: ContactModel, user: User
    ) -> Optional[Contact]:
        """
        Updates an existing contact for the specified user.

        Args:
            contact_id (int): The ID of the contact to update.
            contact_data (ContactModel): The updated data for the contact.
            user (User): The owner of the contact.

        Returns:
            Optional[Contact]: The updated contact if successful, otherwise None.
        """
        return await self.repository.update_contact(contact_id, contact_data, user)

    async def delete_contact(self, contact_id: int, user: User) -> Optional[Contact]:
        """
        Deletes a contact by its ID if it belongs to the specified user.

        Args:
            contact_id (int): The ID of the contact to delete.
            user (User): The owner of the contact.

        Returns:
            Optional[Contact]: The deleted contact if successful, otherwise None.
        """
        return await self.repository.delete_contact(contact_id, user)
