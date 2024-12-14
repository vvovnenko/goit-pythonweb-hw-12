import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import config


class DatabaseSessionManager:
    def __init__(self, url: str):
        """
        Initializes the DatabaseSessionManager with an asynchronous database engine and session maker.

        Args:
            url (str): The database connection URL.
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Provides a context manager for an asynchronous database session.

        Yields:
            AsyncSession: The asynchronous SQLAlchemy session object.

        Raises:
            Exception: If the session maker is not initialized.
            SQLAlchemyError: If a database error occurs, the transaction will be rolled back and the error re-raised.
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise  # Re-raise the original error
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(config.DB_URL)


async def get_db():
    """
    Dependency function for FastAPI routes that provides an asynchronous database session.
    Used with `Depends` to inject the session into route handlers.

    Yields:
        AsyncSession: The asynchronous SQLAlchemy session object.
    """
    async with sessionmanager.session() as session:
        yield session
