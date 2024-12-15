import pytest

from src.database.models import User, UserRole
from tests.conftest import TestingSessionLocal
from sqlalchemy import select


def test_me(client, get_token, test_user_data):
    response = client.get(
        "api/users/me",
        headers={"Authorization": f"Bearer {get_token}"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == test_user_data.get("username")
    assert data["email"] == test_user_data.get("email")
    assert data["avatar"] == test_user_data.get("avatar")
    assert "id" in data


def test_me_unauthenticated(client):
    response = client.get(
        "api/users/me",
    )

    assert response.status_code == 401, response.text


def test_update_avatar_user_with_user_role(
    client, get_token, tmp_path, mocker, test_user_data
):
    test_file = tmp_path / "avatar.jpg"
    test_file.write_bytes(b"fake image content")

    with open(test_file, "rb") as f:
        files = {"file": ("avatar.jpg", f, "image/jpeg")}
        response = client.patch(
            "api/users/avatar",
            headers={"Authorization": f"Bearer {get_token}"},
            files=files,
        )

    assert response.status_code == 403, response.text
    data = response.json()
    assert data["detail"] == "Недостатньо прав доступу"


@pytest.mark.asyncio
async def test_update_avatar_user_with_admin_role(
    client, get_token, tmp_path, mocker, test_user_data
):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == test_user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.role = UserRole.ADMIN
            await session.commit()

    mock_upload_file = mocker.patch(
        "src.service.upload_file.UploadFileService.upload_file"
    )
    mock_upload_file.return_value = "http://example.com/avatar.jpg"

    test_file = tmp_path / "avatar.jpg"
    test_file.write_bytes(b"fake image content")

    with open(test_file, "rb") as f:
        files = {"file": ("avatar.jpg", f, "image/jpeg")}
        response = client.patch(
            "api/users/avatar",
            headers={"Authorization": f"Bearer {get_token}"},
            files=files,
        )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == test_user_data.get("username")
    assert data["email"] == test_user_data.get("email")
    assert data["avatar"] == "http://example.com/avatar.jpg"
    assert "id" in data
