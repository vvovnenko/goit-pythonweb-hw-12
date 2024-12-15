from datetime import date

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.repository.users import UserRepository
from src.schemas.usesrs import UserCreate


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def user_repository(mock_session):
    return UserRepository(mock_session)


@pytest.mark.asyncio
async def test_get_user_by_id(user_repository, mock_session):
    # Setup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(id=1, username="testuser")
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await user_repository.get_user_by_id(user_id=1)

    # Assertions
    assert result is not None
    assert result.id == 1
    assert result.username == "testuser"


@pytest.mark.asyncio
async def test_get_user_by_username(user_repository, mock_session):
    # Setup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(id=1, username="testuser")
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await user_repository.get_user_by_username(username="testuser")

    # Assertions
    assert result is not None
    assert result.id == 1
    assert result.username == "testuser"


@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, mock_session):
    # Setup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(
        id=1, username="testuser", email="testemail@example.com"
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await user_repository.get_user_by_email(email="testemail@example.com")

    # Assertions
    assert result is not None
    assert result.id == 1
    assert result.username == "testuser"
    assert result.email == "testemail@example.com"


@pytest.mark.asyncio
async def test_create_user(user_repository, mock_session):
    # Setup
    user_data = UserCreate(
        username="testuser", email="testemail@example.com", password="hashedpassword"
    )

    # Call method
    result = await user_repository.create_user(
        body=user_data, avatar="https://example.com/test.png"
    )

    # Assertions
    assert isinstance(result, User)
    assert result.username == "testuser"
    assert result.email == "testemail@example.com"
    assert result.hashed_password == "hashedpassword"
    assert result.avatar == "https://example.com/test.png"
    assert result.is_confirmed == False

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_confirmed_email(user_repository, mock_session):
    # Setup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(
        id=1, username="testuser", email="testemail@example.com", is_confirmed=False
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await user_repository.confirmed_email(email="testemail@example.com")

    # Assertions
    assert isinstance(result, User)
    assert result.username == "testuser"
    assert result.email == "testemail@example.com"
    assert result.is_confirmed == True

    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update_avatar_url(user_repository, mock_session):
    # Setup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(
        id=1,
        username="testuser",
        email="testemail@example.com",
        avatar="https://example.com/test.png",
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await user_repository.update_avatar_url(
        email="testemail@example.com", url="https://example.com/test_new.png"
    )

    # Assertions
    assert isinstance(result, User)
    assert result.username == "testuser"
    assert result.email == "testemail@example.com"
    assert result.avatar == "https://example.com/test_new.png"

    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update_avatar_url(user_repository, mock_session):
    # Setup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(
        id=1,
        username="testuser",
        email="testemail@example.com",
        hashed_password="hashed_password",
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await user_repository.reset_password(
        email="testemail@example.com", password="new_hashed_password"
    )

    # Assertions
    assert isinstance(result, User)
    assert result.username == "testuser"
    assert result.email == "testemail@example.com"
    assert result.hashed_password == "new_hashed_password"

    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update_avatar_url_not_found(user_repository, mock_session):
    # Setup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await user_repository.reset_password(
        email="testemail@example.com", password="new_hashed_password"
    )

    # Assertions
    assert result is None

    mock_session.commit.assert_not_called()
    mock_session.refresh.assert_not_called()
