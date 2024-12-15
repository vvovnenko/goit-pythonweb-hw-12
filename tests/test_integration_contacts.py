def test_create_contact(client, get_token):
    response = client.post(
        "api/contacts",
        headers={"Authorization": f"Bearer {get_token}"},
        json={
            "firstname": "John",
            "lastname": "Doe",
            "email": "johndoe@example.com",
            "phone": "11111111",
            "birthday": "1990-01-01",
        },
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["id"] == 1
    assert data["firstname"] == "John"
    assert data["lastname"] == "Doe"
    assert data["email"] == "johndoe@example.com"
    assert data["phone"] == "11111111"
    assert data["birthday"] == "1990-01-01"
    assert data["comment"] is None


def test_read_contact(client, get_token):
    response = client.get(
        "api/contacts/1",
        headers={"Authorization": f"Bearer {get_token}"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == 1
    assert data["firstname"] == "John"
    assert data["lastname"] == "Doe"
    assert data["email"] == "johndoe@example.com"
    assert data["phone"] == "11111111"
    assert data["birthday"] == "1990-01-01"
    assert data["comment"] is None


def test_read_contact_not_found(client, get_token):
    response = client.get(
        "api/contacts/2",
        headers={"Authorization": f"Bearer {get_token}"},
    )

    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found."


def test_read_contacts(client, get_token):
    response = client.get(
        "api/contacts",
        headers={"Authorization": f"Bearer {get_token}"},
    )

    data = response.json()
    assert isinstance(data, list)
    assert data[0]["id"] == 1
    assert data[0]["firstname"] == "John"


def test_update_contact(client, get_token):
    new_contact_data = {
        "firstname": "firstname2",
        "lastname": "lastname2",
        "email": "email2@example.com",
        "phone": "34343434343",
        "birthday": "2003-05-21",
        "comment": "brand new comment",
    }

    response = client.put(
        "api/contacts/1",
        headers={"Authorization": f"Bearer {get_token}"},
        json=new_contact_data,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == 1
    assert data["firstname"] == new_contact_data["firstname"]
    assert data["lastname"] == new_contact_data["lastname"]
    assert data["email"] == new_contact_data["email"]
    assert data["phone"] == new_contact_data["phone"]
    assert data["birthday"] == new_contact_data["birthday"]
    assert data["comment"] == new_contact_data.get("comment")


def test_update_contact_not_found(client, get_token):
    new_contact_data = {
        "firstname": "firstname2",
        "lastname": "lastname2",
        "email": "email2@example.com",
        "phone": "34343434343",
        "birthday": "2003-05-21",
        "comment": "brand new comment",
    }

    response = client.put(
        "api/contacts/2",
        headers={"Authorization": f"Bearer {get_token}"},
        json=new_contact_data,
    )

    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found."


def test_delete_contact(client, get_token):
    response = client.delete(
        "api/contacts/1",
        headers={"Authorization": f"Bearer {get_token}"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == 1


def test_repeat_delete_contact(client, get_token):
    response = client.delete(
        "api/contacts/2",
        headers={"Authorization": f"Bearer {get_token}"},
    )

    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found."
