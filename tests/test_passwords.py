from typing import cast

import mysql.connector

from app.core.config import settings


def test_create_password(authenticated_client):
    response = authenticated_client.post("/passwords", json={"name": "GitHub", "username": "mikolaj@example.com", "password": "SuperTajneHaslo123!"})

    assert response.status_code == 201

    data = response.json()

    password_id = cast(int, data["id"])

    assert password_id > 0
    assert data["name"] == "GitHub"
    assert data["username"] == "mikolaj@example.com"
    assert data["password"] == "SuperTajneHaslo123!"


def test_password_is_encrypted_in_database(authenticated_client):
    response = authenticated_client.post("/passwords", json={"name": "GitHub", "username": "mikolaj@example.com", "password": "SuperTajneHaslo123!"})

    assert response.status_code == 201

    password_id = cast(int, response.json()["id"])

    connection = mysql.connector.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
    )

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id, name, username, nonce, ciphertext FROM passwords WHERE id = %s", (password_id,))
        password = cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

    assert password is not None
    assert password["id"] == password_id
    assert password["name"] == "GitHub"
    assert password["username"] == "mikolaj@example.com"
    assert password["nonce"] != ""
    assert password["ciphertext"] != ""
    assert password["ciphertext"] != "SuperTajneHaslo123!"


def test_get_passwords(authenticated_client):
    authenticated_client.post("/passwords", json={"name": "GitHub", "username": "mikolaj@example.com", "password": "GitHubPassword!"})
    authenticated_client.post("/passwords", json={"name": "Gmail", "username": "mikolaj@gmail.com", "password": "GmailPassword!"})

    response = authenticated_client.get("/passwords")

    assert response.status_code == 200

    passwords = response.json()

    assert len(passwords) == 2

    assert passwords[0]["name"] == "GitHub"
    assert passwords[0]["username"] == "mikolaj@example.com"

    assert passwords[1]["name"] == "Gmail"
    assert passwords[1]["username"] == "mikolaj@gmail.com"

    assert "password" not in passwords[0]
    assert "password" not in passwords[1]


def test_get_password(authenticated_client):
    create_response = authenticated_client.post("/passwords", json={"name": "GitHub", "username": "mikolaj@example.com", "password": "SuperTajneHaslo123!"})

    password_id = cast(int, create_response.json()["id"])

    response = authenticated_client.get(f"/passwords/{password_id}")

    assert response.status_code == 200

    assert response.json() == {
        "id": password_id,
        "name": "GitHub",
        "username": "mikolaj@example.com",
        "password": "SuperTajneHaslo123!",
    }


def test_get_nonexistent_password(authenticated_client):
    response = authenticated_client.get("/passwords/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Password not found"}


def test_update_password(authenticated_client):
    create_response = authenticated_client.post("/passwords", json={"name": "GitHub", "username": "old@example.com", "password": "OldPassword123!"})

    password_id = cast(int, create_response.json()["id"])

    response = authenticated_client.put(f"/passwords/{password_id}", json={"name": "GitHub Updated", "username": "new@example.com", "password": "NewPassword456!"})

    assert response.status_code == 200

    assert response.json() == {
        "id": password_id,
        "name": "GitHub Updated",
        "username": "new@example.com",
        "password": "NewPassword456!",
    }


def test_update_password_changes_ciphertext(authenticated_client):
    create_response = authenticated_client.post("/passwords", json={"name": "GitHub", "username": "old@example.com", "password": "OldPassword123!"})

    password_id = cast(int, create_response.json()["id"])

    connection = mysql.connector.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
    )

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT ciphertext FROM passwords WHERE id = %s", (password_id,))
        password_before = cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

    response = authenticated_client.put(f"/passwords/{password_id}", json={"name": "GitHub Updated", "username": "new@example.com", "password": "NewPassword456!"})

    assert response.status_code == 200

    connection = mysql.connector.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
    )

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT ciphertext FROM passwords WHERE id = %s", (password_id,))
        password_after = cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

    assert password_before is not None
    assert password_after is not None
    assert password_before["ciphertext"] != password_after["ciphertext"]


def test_update_nonexistent_password(authenticated_client):
    response = authenticated_client.put("/passwords/999999", json={"name": "GitHub", "username": "mikolaj@example.com", "password": "NewPassword123!"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Password not found"}


def test_unauthenticated_user_cannot_access_passwords(client):
    response = client.get("/passwords")

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired session"}


def test_delete_password(authenticated_client):
    create_response = authenticated_client.post(
        "/passwords",
        json={
            "name": "GitHub",
            "username": "mikolaj@example.com",
            "password": "SuperTajneHaslo123!",
        },
    )

    password_id = cast(int, create_response.json()["id"])

    response = authenticated_client.delete(f"/passwords/{password_id}")

    assert response.status_code == 204

    get_response = authenticated_client.get(f"/passwords/{password_id}")

    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "Password not found"}


def test_delete_nonexistent_password(authenticated_client):
    response = authenticated_client.delete("/passwords/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Password not found"}