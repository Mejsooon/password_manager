import bcrypt

from app.models.models import User
from app.repositories import user_repository
from app.schemas.auth import UserCreate


class UsernameAlreadyExistsError(Exception):
    pass


def authenticate(username: str, password: str) -> User | None:
    user = user_repository.find_by_username(username)

    if user is None:
        return None

    password_matches = bcrypt.checkpw(
        password.encode("utf-8"),
        user.password_hash.encode("utf-8"),
    )

    if not password_matches:
        return None

    return user


def register_user(user_data: UserCreate) -> User:
    existing_user = user_repository.find_by_username(user_data.username)

    if existing_user is not None:
        raise UsernameAlreadyExistsError(
            "Nazwa użytkownika jest już zajęta."
        )

    password_hash = bcrypt.hashpw(
        user_data.password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")

    user = User(
        id=None,
        username=user_data.username,
        password_hash=password_hash,
        created_at=None,
    )

    return user_repository.save(user)