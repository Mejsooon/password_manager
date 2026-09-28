from app.core.database import execute
from app.models.models import Password


def row_to_password(row: dict) -> Password:
    return Password(
        id=row["id"],
        user_id=row["user_id"],
        name=row["name"],
        username=row["username"],
        nonce=row["nonce"],
        ciphertext=row["ciphertext"],
        created_at=row["created_at"],
    )

def find_by_id(password_id: int, user_id: int) -> Password | None:
    row=execute("SELECT id, user_id, name, username, nonce, ciphertext, created_at FROM passwords WHERE id = %s AND user_id = %s", (password_id, user_id), fetch="one")

    if row is None:
        return None

    return row_to_password(row)


def find_all_by_user_id(user_id: int) -> list[Password]:
    rows = execute("SELECT id, user_id, name, username, nonce, ciphertext, created_at FROM passwords WHERE user_id = %s ORDER BY id", (user_id,), fetch="all")

    return [row_to_password(row) for row in rows]


def save(password: Password) -> Password:
    new_id = execute("INSERT INTO passwords (user_id, name, username, nonce, ciphertext) VALUES (%s, %s, %s, %s, %s)", (password.user_id, password.name, password.username, password.nonce, password.ciphertext))

    return Password(
        id=int(new_id),
        user_id=password.user_id,
        name=password.name,
        username=password.username,
        nonce=password.nonce,
        ciphertext=password.ciphertext,
        created_at=password.created_at,
    )

def delete_by_id(password_id: int, user_id: int) -> bool:
    execute("DELETE FROM passwords WHERE id = %s AND user_id = %s", (password_id, user_id))
    return True