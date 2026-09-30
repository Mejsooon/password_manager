import mysql.connector
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient


load_dotenv(".env.test", override=True)


from app.core.config import settings
from app.main import app


@pytest.fixture(autouse=True)
def clean_database():
    connection = mysql.connector.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
    )

    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM passwords")
        cursor.execute("DELETE FROM sessions")
        cursor.execute("DELETE FROM users")

        connection.commit()

        yield

    finally:
        cursor.close()
        connection.close()


@pytest.fixture
def client(clean_database):
    with TestClient(app, base_url="https://testserver",) as test_client:
        yield test_client