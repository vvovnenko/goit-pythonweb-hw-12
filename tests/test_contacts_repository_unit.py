from datetime import date

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactsRepository
from src.schemas.contacts import ContactModel


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contact_repository(mock_session):
    return ContactsRepository(mock_session)


@pytest.fixture
def user():
    return User(id=1, username="testuser")


@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, user):
    # Setup
    contact_data = ContactModel(
        firstname="John",
        lastname="Doe",
        email="johndoe@example.com",
        phone="1234567890",
        birthday=date(1990, 1, 1),
        comment="Friend from college",
    )

    # Call method
    result = await contact_repository.create_contact(body=contact_data, user=user)

    # Assertions
    assert isinstance(result, Contact)
    assert result.firstname == "John"
    assert result.lastname == "Doe"
    assert result.email == "johndoe@example.com"
    assert result.phone == "1234567890"
    assert result.birthday == date(1990, 1, 1)
    assert result.comment == "Friend from college"
    assert result.user == user

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_read_contacts(contact_repository, mock_session, user):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(firstname="John", lastname="Doe", email="johndoe@example.com"),
        Contact(firstname="Jane", lastname="Doe", email="janedoe@example.com"),
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contacts = await contact_repository.read_contacts(user=user)

    # Assertions
    assert len(contacts) == 2


@pytest.mark.asyncio
async def test_read_contact(contact_repository, mock_session, user):
    # Setup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(
        firstname="John", lastname="Doe", email="johndoe@example.com"
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.read_contact(contact_id=1, user=user)

    # Assertions
    assert result is not None
    assert result.lastname == "Doe"
    assert result.email == "johndoe@example.com"


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user):
    # Setup
    contact_data = ContactModel(
        firstname="John",
        lastname="Doe",
        email="johndoe@example.com",
        phone="1234567890",
        birthday=date(1990, 1, 1),
        comment="Friend from college",
    )
    existing_contact = Contact(
        id=1,
        firstname="Colin",
        lastname="Farrel",
        email="colinfarrel@example.com",
        phone="9898989898",
        birthday=date(1982, 1, 1),
        comment="Some dude",
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.update_contact(
        contact_id=1, body=contact_data, user=user
    )

    # Assertions
    assert result.firstname == "John"
    assert result.lastname == "Doe"
    assert result.email == "johndoe@example.com"
    assert result.phone == "1234567890"
    assert result.birthday == date(1990, 1, 1)
    assert result.comment == "Friend from college"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_contact)


@pytest.mark.asyncio
async def test_delete_contact(contact_repository, mock_session, user):
    # Setup
    existing_contact = Contact(
        id=1,
        firstname="Colin",
        lastname="Farrel",
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.delete_contact(contact_id=1, user=user)

    # Assertions
    assert result is not None
    assert result.id == 1
    assert result.firstname == "Colin"
    assert result.lastname == "Farrel"
    mock_session.delete.assert_awaited_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()
