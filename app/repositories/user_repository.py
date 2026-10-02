from app.core.database import execute
from app.models.models import User


def row_to_user(row: dict) -> User:
    return User(
        id=row["id"],
        username=row["username"],
        password_hash=row["password_hash"],
        created_at=row["created_at"],
    )


def find_by_username(username: str) -> User | None:
    row = execute(
        "SELECT id, username, password_hash, created_at "
        "FROM users WHERE username = %s",
        (username,),
        fetch="one",
    )

    if row is None:
        return None

    return row_to_user(row)


def find_by_id(user_id: int) -> User | None:
    row = execute(
        "SELECT id, username, password_hash, created_at "
        "FROM users WHERE id = %s",
        (user_id,),
        fetch="one",
    )

    if row is None:
        return None

    return row_to_user(row)


def save(user: User) -> User:
    new_id = execute(
        "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
        (user.username, user.password_hash),
    )

    return User(
        id=int(new_id),
        username=user.username,
        password_hash=user.password_hash,
        created_at=user.created_at,
    )