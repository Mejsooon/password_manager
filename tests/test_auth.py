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
        database=settings.db_name,
    )

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id, username, password_hash FROM users WHERE username = %s",
            ("mikolaj",),
        )

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
    assert response.json() == {"detail": "Username already exists"}


def test_login(client):
    register_response = client.post("/auth/register", json={"username": "mikolaj", "password": "Test123!"})

    user_id = cast(int, register_response.json()["id"])

    response = client.post("/auth/login", json={"username": "mikolaj", "password": "Test123!"})

    assert response.status_code == 200
    assert response.json() == {
        "id": user_id,
        "username": "mikolaj",
    }

    assert "session_token" in client.cookies


def test_session_token_is_stored_as_hash(client):
    client.post("/auth/register", json={"username": "mikolaj", "password": "Test123!"})

    response = client.post("/auth/login", json={"username": "mikolaj", "password": "Test123!"})

    assert response.status_code == 200

    session_token = client.cookies.get("session_token")

    assert session_token is not None
    assert session_token != ""

    connection = mysql.connector.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
    )

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT token_hash FROM sessions WHERE user_id = %s",
            (response.json()["id"],),
        )

        session = cursor.fetchone()

    finally:
        cursor.close()
        connection.close()

    assert session is not None
    assert session["token_hash"] != session_token
    assert len(session["token_hash"]) == 64


def test_login_wrong_password(client):
    client.post("/auth/register", json={"username": "mikolaj", "password": "Test123!"})

    response = client.post("/auth/login", json={"username": "mikolaj", "password": "WrongPassword!"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}
    assert "session_token" not in client.cookies


def test_current_user(client):
    register_response = client.post("/auth/register", json={"username": "mikolaj", "password": "Test123!"})

    user_id = cast(int, register_response.json()["id"])

    login_response = client.post("/auth/login", json={"username": "mikolaj", "password": "Test123!"})

    assert login_response.status_code == 200
    assert "session_token" in client.cookies

    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json() == {
        "id": user_id,
        "username": "mikolaj",
    }


def test_current_user_without_session(client):
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired session"}


def test_logout(client):
    client.post("/auth/register", json={"username": "mikolaj", "password": "Test123!"})
    client.post("/auth/login", json={"username": "mikolaj", "password": "Test123!"})

    session_token = client.cookies.get("session_token")

    assert session_token is not None

    response = client.post("/auth/logout")

    assert response.status_code == 204
    assert "session_token" not in client.cookies

    me_response = client.get("/auth/me")

    assert me_response.status_code == 401
    assert me_response.json() == {"detail": "Invalid or expired session"}

    connection = mysql.connector.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
    )

    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT COUNT(*) FROM sessions WHERE token_hash = SHA2(%s, 256)",
            (session_token,),
        )

        session_count = cursor.fetchone()[0]

    finally:
        cursor.close()
        connection.close()

    assert session_count == 0