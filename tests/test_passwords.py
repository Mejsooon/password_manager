from typing import cast
import mysql.connector
from app.core.config import settings


def test_create_password(authenticated_client):
    response = authenticated_client.post("/passwords", json={"name": "GitHub", "username": "mikolaj@example.com",
                                                             "password": "SuperTajneHaslo123!"})

    assert response.status_code == 201

    data = response.json()
    password_id = cast(int, data["id"])

    assert password_id > 0
    assert data["name"] == "GitHub"
    assert data["username"] == "mikolaj@example.com"
    assert data["password"] == "SuperTajneHaslo123!"

    connection = mysql.connector.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name)

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id, user_id, name, username, nonce, ciphertext FROM passwords WHERE id = %s",
                       (password_id,))
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
    authenticated_client.post("/passwords",
                              json={"name": "GitHub", "username": "mikolaj@example.com", "password": "GitHubPassword!"})

    authenticated_client.post("/passwords",
                              json={"name": "Gmail", "username": "mikolaj@gmail.com", "password": "GmailPassword!"})

    response = authenticated_client.get("/passwords")

    assert response.status_code == 200

    passwords = response.json()

    assert len(passwords) == 2
    assert passwords[0]["name"] == "GitHub"
    assert passwords[0]["username"] == "mikolaj@example.com"
    assert passwords[0]["password"] == "GitHubPassword!"
    assert passwords[1]["name"] == "Gmail"
    assert passwords[1]["username"] == "mikolaj@gmail.com"
    assert passwords[1]["password"] == "GmailPassword!"


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


def test_search_passwords(authenticated_client):
    authenticated_client.post("/passwords", json={"name": "GitHub", "username": "mikolaj@example.com", "password": "GitHubPassword!"})
    authenticated_client.post("/passwords", json={"name": "Gmail", "username": "mikolaj@gmail.com", "password": "GmailPassword!"})

    response = authenticated_client.get("/passwords?q=GitHub")

    assert response.status_code == 200

    passwords = response.json()

    assert len(passwords) == 1
    assert passwords[0]["name"] == "GitHub"
    assert passwords[0]["username"] == "mikolaj@example.com"
    assert passwords[0]["password"] == "GitHubPassword!"


def test_search_passwords_by_username(authenticated_client):
    authenticated_client.post("/passwords", json={"name": "GitHub", "username": "mikolaj@example.com", "password": "GitHubPassword!"})
    authenticated_client.post("/passwords", json={"name": "Gmail", "username": "mikolaj@gmail.com", "password": "GmailPassword!"})

    response = authenticated_client.get("/passwords?q=example.com")

    assert response.status_code == 200

    passwords = response.json()

    assert len(passwords) == 1
    assert passwords[0]["name"] == "GitHub"
    assert passwords[0]["username"] == "mikolaj@example.com"
    assert passwords[0]["password"] == "GitHubPassword!"


def test_search_passwords_no_results(authenticated_client):
    authenticated_client.post("/passwords", json={"name": "GitHub", "username": "mikolaj@example.com", "password": "GitHubPassword!"})

    response = authenticated_client.get("/passwords?q=Facebook")

    assert response.status_code == 200
    assert response.json() == []


def test_get_nonexistent_password(authenticated_client):
    response = authenticated_client.get("/passwords/999999")

    assert response.status_code == 404

    assert response.json() == {"detail": "Password not found"}


def test_delete_password(authenticated_client):
    create_response = authenticated_client.post("/passwords", json={"name": "GitHub", "username": "mikolaj@example.com", "password": "SuperTajneHaslo123!"})

    password_id = cast(int, create_response.json()["id"])

    response = authenticated_client.delete(f"/passwords/{password_id}")

    assert response.status_code == 204

    get_response = authenticated_client.get(f"/passwords/{password_id}")

    assert get_response.status_code == 404


def test_user_isolation(client):
    client.post("/auth/register", json={"username": "mikolaj", "password": "Test123!"})

    client.post("/auth/login", json={"username": "mikolaj", "password": "Test123!"})

    create_response = client.post("/passwords", json={"name": "GitHub", "username": "mikolaj@example.com", "password": "MikolajPassword!"})

    password_id = cast(int, create_response.json()["id"])

    client.post("/auth/logout")

    client.post("/auth/register", json={"username": "jan", "password": "Test456!"})

    client.post("/auth/login", json={"username": "jan", "password": "Test456!"})

    response = client.get(f"/passwords/{password_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Password not found"}


def test_unauthenticated_user_cannot_access_passwords(client):
    response = client.get("/passwords")

    assert response.status_code == 401


def test_update_password(authenticated_client):
    create_response = authenticated_client.post("/passwords",json={"name": "GitHub", "username": "old@example.com", "password": "OldPassword123!",})

    password_id = cast(int, create_response.json()["id"])

    response = authenticated_client.put(f"/passwords/{password_id}", json={"name": "GitHub Updated", "username": "new@example.com", "password": "NewPassword456!",})

    assert response.status_code == 200

    assert response.json() == {
        "id": password_id,
        "name": "GitHub Updated",
        "username": "new@example.com",
        "password": "NewPassword456!",
    }


def test_passwords_limit(authenticated_client):
    authenticated_client.post("/passwords", json={"name": "GitHub", "username": "github@example.com", "password": "GitHubPassword!"})
    authenticated_client.post("/passwords", json={"name": "Gmail", "username": "gmail@example.com", "password": "GmailPassword!"})
    authenticated_client.post("/passwords", json={"name": "Discord", "username": "discord@example.com", "password": "DiscordPassword!"})

    response = authenticated_client.get("/passwords?limit=2")

    assert response.status_code == 200

    passwords = response.json()

    assert len(passwords) == 2
    assert passwords[0]["name"] == "GitHub"
    assert passwords[1]["name"] == "Gmail"


def test_passwords_offset(authenticated_client):
    authenticated_client.post("/passwords", json={"name": "GitHub", "username": "github@example.com", "password": "GitHubPassword!"})
    authenticated_client.post("/passwords", json={"name": "Gmail", "username": "gmail@example.com", "password": "GmailPassword!"})
    authenticated_client.post("/passwords", json={"name": "Discord", "username": "discord@example.com", "password": "DiscordPassword!"})

    response = authenticated_client.get("/passwords?limit=2&offset=1")

    assert response.status_code == 200

    passwords = response.json()

    assert len(passwords) == 2
    assert passwords[0]["name"] == "Gmail"
    assert passwords[1]["name"] == "Discord"


def test_search_passwords_with_pagination(authenticated_client):
    authenticated_client.post("/passwords", json={"name": "GitHub", "username": "github1@example.com", "password": "Password1!"})
    authenticated_client.post("/passwords", json={"name": "GitLab", "username": "gitlab@example.com", "password": "Password2!"})
    authenticated_client.post("/passwords", json={"name": "Gmail", "username": "gmail@example.com", "password": "Password3!"})
    authenticated_client.post("/passwords", json={"name": "GitKraken", "username": "gitkraken@example.com", "password": "Password4!"})

    response = authenticated_client.get("/passwords?q=Git&limit=2&offset=1")

    assert response.status_code == 200

    passwords = response.json()

    assert len(passwords) == 2
    assert passwords[0]["name"] == "GitLab"
    assert passwords[1]["name"] == "GitKraken"


def test_passwords_invalid_pagination(authenticated_client):
    response = authenticated_client.get("/passwords?limit=0")

    assert response.status_code == 422

    response = authenticated_client.get("/passwords?limit=101")

    assert response.status_code == 422

    response = authenticated_client.get("/passwords?offset=-1")

    assert response.status_code == 422