from typing import cast
import mysql.connector
from app.core.config import settings


def test_register_user(client):
    response = client.post("/auth/register", json={"username": "mikolaj", "password": "Test123!"})

    assert response.status_code == 201
    data = response.json()

    user_id = cast(int, data["id"])

    assert isinstance(data["id"], int)

    assert data["id"] > 0

    assert data["username"] == "mikolaj"

    connection = mysql.connector.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name)

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id, username, password_hash FROM users WHERE username = %s", ("mikolaj",))

        user = cursor.fetchone()

    finally:
        cursor.close()

        connection.close()

    assert user is not None

    assert user["id"] == user_id

    assert user["username"] == "mikolaj"

    assert user["password_hash"] != "Test123!"

    assert user["password_hash"].startswith("$2")


def test_register_duplicate_username(client):
    client.post("/auth/register", json={"username": "mikolaj", "password": "Test123!"})

    response = client.post("/auth/register", json={"username": "mikolaj", "password": "AnotherPassword!"})

    assert response.status_code == 409

    assert response.json() == {"detail": "Nazwa użytkownika jest już zajęta"}


def test_login(client):
    register_response = client.post("/auth/register", json={"username": "mikolaj", "password": "Test123!"})

    user_id = cast(int, register_response.json()["id"])

    response = client.post("/auth/login", json={"username": "mikolaj", "password": "Test123!"})

    assert response.status_code == 200

    assert response.json() == {"id": user_id, "username": "mikolaj"}

    assert "session_token" in client.cookies


def test_login_wrong_password(client):
    client.post("/auth/register", json={"username": "mikolaj", "password": "Test123!"})

    response = client.post("/auth/login", json={"username": "mikolaj", "password": "WrongPassword!"})

    assert response.status_code == 401

    assert response.json() == {"detail": "Incorrect username or password"}

    assert "session_token" not in client.cookies


def test_current_user_and_logout(client):
    register_response = client.post("/auth/register", json={"username": "mikolaj", "password": "Test123!"})

    user_id = cast(int, register_response.json()["id"])

    login_response = client.post("/auth/login", json={"username": "mikolaj", "password": "Test123!"})

    assert login_response.status_code == 200

    assert login_response.json() == {"id": user_id, "username": "mikolaj"}

    assert "session_token" in client.cookies

    me_response = client.get("/auth/me")

    assert me_response.status_code == 200

    assert me_response.json() == {"id": user_id, "username": "mikolaj"}

    logout_response = client.post("/auth/logout")

    assert logout_response.status_code == 204

    me_response_after_logout = client.get("/auth/me")

    assert me_response_after_logout.status_code == 401