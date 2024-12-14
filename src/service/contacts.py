from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactsRepository
from src.schemas.contacts import ContactModel


class ContactService:
    def __init__(self, db_session: AsyncSession):
        self.repository = ContactsRepository(db_session)

    async def create_contact(self, contact_data: ContactModel, user: User) -> Contact:
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
        return await self.repository.read_contacts(
            user, firstname, lastname, email, upcoming_birthday_days, skip, limit
        )

    async def read_contact(self, contact_id: int, user: User) -> Optional[Contact]:
        return await self.repository.read_contact(contact_id, user)

    async def update_contact(
        self, contact_id: int, contact_data: ContactModel, user: User
    ):
        return await self.repository.update_contact(contact_id, contact_data, user)

    async def delete_contact(self, contact_id: int, user: User) -> Optional[Contact]:
        return await self.repository.delete_contact(contact_id, user)
