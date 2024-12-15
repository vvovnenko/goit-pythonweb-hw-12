from unittest.mock import Mock

from src.service.auth import create_email_token, create_reset_password_token, Hash

user_data = {
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
    "role": "user",
}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Користувач з таким email вже існує"


def test_not_confirmed_login(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Електронна адреса не підтверджена"


def test_request_email(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post(
        "api/auth/request_email", json={"email": user_data.get("email")}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Check your email for confirmation."


def test_confirm_email(client):
    token_verification = create_email_token({"sub": user_data.get("email")})
    response = client.get(f"api/auth/confirmed_email/{token_verification}")

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Your email has been confirmed."


def test_confirmed_request_email(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post(
        "api/auth/request_email", json={"email": user_data.get("email")}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Your email has already been confirmed."


def test_repeat_confirm_email(client):
    token_verification = create_email_token({"sub": user_data.get("email")})
    response = client.get(f"api/auth/confirmed_email/{token_verification}")

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Your email has already been confirmed."


def test_confirm_email_with_invalid_token(client):
    token_verification = "invalid_token"
    response = client.get(f"api/auth/confirmed_email/{token_verification}")

    assert response.status_code == 422, response.text
    data = response.json()
    assert data["detail"] == "Incorrect token."


def test_confirm_email_with_unregistered_email(client):
    token_verification = create_email_token({"sub": "unknown@email.com"})
    response = client.get(f"api/auth/confirmed_email/{token_verification}")

    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Verification error"


def test_login(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data


def test_wrong_password_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": user_data.get("username"), "password": "password"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Неправильний логін або пароль"


def test_wrong_username_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": "username", "password": user_data.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Неправильний логін або пароль"


def test_validation_error_login(client):
    response = client.post(
        "api/auth/login", data={"password": user_data.get("password")}
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


def test_reset_password_request_with_unregistered_email(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post(
        "api/auth/reset_password",
        json={"email": "unknown@email.com", "password": "new_password"},
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Your email is not registered"


def test_reset_password_request(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post(
        "api/auth/reset_password",
        json={"email": user_data.get("email"), "password": "new_password"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Check your email for confirmation"


def test_confirm_reset_password(client):
    password = "new_password_1233"
    hashed_password = Hash().get_password_hash(password)
    token = create_reset_password_token(user_data.get("email"), hashed_password)
    response = client.get(f"api/auth/confirm_reset_password/{token}")

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Password reset successful"

    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": password,
        },
    )
    assert response.status_code == 200, response.text
