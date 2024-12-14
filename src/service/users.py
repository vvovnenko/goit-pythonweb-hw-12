from libgravatar import Gravatar
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.users import UserRepository
from src.schemas.usesrs import UserCreate


class UserService:
    def __init__(self, db: AsyncSession):
        """
        Initializes the UserService with the provided database session.

        Args:
            db (AsyncSession): The asynchronous SQLAlchemy session for database operations.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Creates a new user and associates a Gravatar avatar if available.

        Args:
            body (UserCreate): The data for the new user.

        Returns:
            User: The newly created user instance.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Retrieves a user by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            Optional[User]: The user instance if found, otherwise None.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Retrieves a user by their username.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            Optional[User]: The user instance if found, otherwise None.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Retrieves a user by their email address.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            Optional[User]: The user instance if found, otherwise None.
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str):
        """
        Updates the user's email to a confirmed state.

        Args:
            email (str): The email address to confirm.

        Returns:
            Optional[User]: The updated user if the operation was successful, otherwise None.
        """
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """
        Updates the avatar URL for a user identified by their email.

        Args:
            email (str): The email address of the user whose avatar will be updated.
            url (str): The new avatar URL.

        Returns:
            Optional[User]: The updated user if the operation was successful, otherwise None.
        """
        return await self.repository.update_avatar_url(email, url)
