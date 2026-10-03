from app.core.database import execute
from app.models.models import Session


def row_to_session(row: dict) -> Session:
    return Session(
        id=row["id"],
        user_id=row["user_id"],
        token_hash=row["token_hash"],
        expires_at=row["expires_at"],
        created_at=row["created_at"],
    )


def find_by_token_hash(token_hash: str) -> Session | None:
    row = execute("SELECT id, user_id, token_hash, expires_at, created_at FROM sessions WHERE token_hash = %s",
        (token_hash,),fetch="one")

    if row is None:
        return None

    return row_to_session(row)


def delete_by_token_hash(token_hash: str) -> None:
    execute("DELETE FROM sessions WHERE token_hash = %s",(token_hash,))


def save(session: Session) -> Session:
    new_id = execute("INSERT INTO sessions (user_id, token_hash, expires_at) VALUES (%s, %s, %s)",
        (session.user_id, session.token_hash, session.expires_at))

    return Session(
        id=int(new_id),
        user_id=session.user_id,
        token_hash=session.token_hash,
        expires_at=session.expires_at,
        created_at=session.created_at,
    )