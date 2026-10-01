from app.crypto.password_crypto import decrypt_password, encrypt_password
from app.models.models import User, Password, DecryptedPassword
from app.repositories import password_repository
from app.schemas.password import PasswordCreate
from app.core.exceptions import PasswordNotFoundError


def _decrypt_password(password: Password) -> DecryptedPassword:
    return DecryptedPassword(
        id=password.id,
        user_id=password.user_id,
        name=password.name,
        username=password.username,
        password=decrypt_password(password.nonce, password.ciphertext),
        created_at=password.created_at,
    )


def create_password(current_user: User, password_data: PasswordCreate) -> Password:
    encrypted_data = encrypt_password(password_data.password)

    password = Password(
        id=None,
        user_id=current_user.id,
        name=password_data.name,
        username=password_data.username,
        nonce=encrypted_data["nonce"],
        ciphertext=encrypted_data["ciphertext"],
        created_at=None
    )

    return password_repository.save(password)


def get_passwords(
    current_user: User,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Password]:

    return password_repository.find_all_by_user_id(
        user_id=current_user.id,
        search=search,
        limit=limit,
        offset=offset,
    )


def get_password(current_user: User, password_id: int) -> DecryptedPassword:
    password = password_repository.find_by_id(
        password_id=password_id,
        user_id=current_user.id,
    )

    if password is None:
        raise PasswordNotFoundError()

    return _decrypt_password(password)


def delete_password(current_user: User, password_id: int) -> None:
    password = password_repository.find_by_id(password_id=password_id, user_id=current_user.id)

    if password is None:
        raise PasswordNotFoundError()

    password_repository.delete_by_id(password_id=password_id, user_id=current_user.id)


def update_password(current_user: User, password_id: int, password_data: PasswordCreate) -> Password:
    password = password_repository.find_by_id(password_id=password_id, user_id=current_user.id,)

    if password is None:
        raise PasswordNotFoundError()

    encrypted_data = encrypt_password(password_data.password)

    password.name = password_data.name
    password.username = password_data.username
    password.nonce = encrypted_data["nonce"]
    password.ciphertext = encrypted_data["ciphertext"]

    return password_repository.update(password)