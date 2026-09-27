import logging

import mysql.connector
from mysql.connector import MySQLConnection, errorcode

from app.core.config import settings


logger = logging.getLogger(__name__)


def get_connection() -> MySQLConnection:
    return mysql.connector.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
    )


def execute(
    query: str,
    params: tuple = (),
    fetch: str | None = None,
):
    connection = None
    cursor = None

    try:
        connection = get_connection()

        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)

        if fetch == "one":
            return cursor.fetchone()

        if fetch == "all":
            return cursor.fetchall()

        connection.commit()

        return cursor.lastrowid

    except mysql.connector.IntegrityError as exc:
        if connection:
            connection.rollback()

        if exc.errno == errorcode.ER_DUP_ENTRY:
            logger.warning("Duplikat rekordu: %s", exc)

        raise

    except mysql.connector.Error as exc:
        if connection:
            connection.rollback()

        logger.error("Błąd MySQL: %s", exc)

        raise

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()