from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.usesrs import UserCreate
from src.database.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        """
        Initialize the UserRepository with a database session.

        Args:
            session (AsyncSession): The asynchronous database session to be used for database operations.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Get a user by ID.

        Args:
            user_id (int): The ID of the user to get.

        Returns:
            User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Get a user by username.

        Args:
            username (str): The username of the user to get.

        Returns:
            User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Get a user by email.

        Args:
            email (str): The email of the user to get.

        Returns:
            User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Create a new user.

        Args:
            body (UserCreate): The user data to create.
            avatar (str, optional): The URL of the user's avatar. Defaults to None.

        Returns:
            User: The created user.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar,
            is_confirmed=False,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> User:
        """
        Confirm a user's email address.

        Args:
            email (str): The email of the user to confirm.

        Returns:
            None
        """
        user = await self.get_user_by_email(email)
        user.is_confirmed = True
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Update the avatar URL of a user.

        Args:
            email (str): The email of the user to update.
            url (str): The new avatar URL.

        Returns:
            User: The updated user.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user
