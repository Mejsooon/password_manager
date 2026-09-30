import bcrypt

from app.models.models import User, Session
from app.repositories import user_repository, session_repository
from app.schemas.auth import UserCreate

from app.core.exceptions import (InvalidCredentialsError, SessionInvalidError, UsernameAlreadyExistsError)

import hashlib
import secrets
from datetime import datetime, timedelta, timezone


def register_user(user_data: UserCreate) -> User:
    existing_user = user_repository.find_by_username(user_data.username)

    if existing_user is not None:
        raise UsernameAlreadyExistsError()

    password_hash = bcrypt.hashpw(user_data.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    user = User(id = None, username=user_data.username, password_hash=password_hash, created_at=None)

    return user_repository.save(user)


def authenticate(username: str, password: str) -> User | None:
    user = user_repository.find_by_username(username)

    if user is None:
        raise InvalidCredentialsError()

    password_matches = bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8"))

    if not password_matches:
        raise InvalidCredentialsError()

    return user


SESSION_DURATION = timedelta(days=7)

def create_session(user_id: int) -> str:

    session_token = secrets.token_urlsafe(32)

    token_hash = hashlib.sha256(session_token.encode("utf-8")).hexdigest()

    expires_at = (datetime.now(timezone.utc) + SESSION_DURATION).replace(tzinfo=None)

    session = Session(id=None, user_id=user_id, token_hash=token_hash, expires_at=expires_at, created_at=None)

    session_repository.save(session)

    return session_token


def logout(session_token: str) -> None:
    token_hash = hashlib.sha256(session_token.encode("utf-8")).hexdigest()

    session_repository.delete_by_token_hash(token_hash)


def get_current_user(session_token: str) -> User | None:

    token_hash = hashlib.sha256(session_token.encode("utf-8")).hexdigest()

    session = session_repository.find_by_token_hash(token_hash)

    if session is None:
        return None

    current_time = datetime.now(timezone.utc).replace(tzinfo=None)

    if session.expires_at <= current_time:
        session_repository.delete_by_token_hash(token_hash)
        raise SessionInvalidError()

    return user_repository.find_by_id(session.user_id)