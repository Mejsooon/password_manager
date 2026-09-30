from app.crypto.password_crypto import decrypt_password, encrypt_password
from app.models.models import User, Password
from app.repositories import password_repository
from app.schemas.password import PasswordCreate
from app.core.exceptions import PasswordNotFoundError


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


def get_passwords(current_user: User) -> list[Password]:
    passwords = password_repository.find_all_by_user_id(user_id=current_user.id)

    for password in passwords:
        password.ciphertext = decrypt_password(password.nonce, password.ciphertext)

    return passwords


def get_password(current_user: User, password_id: int) -> Password:
    password = password_repository.find_by_id(password_id=password_id, user_id=current_user.id)

    if password is None:
        raise PasswordNotFoundError()

    password.ciphertext = decrypt_password(password.nonce, password.ciphertext)

    return password


def delete_password(current_user: User, password_id: int) -> None:
    password = password_repository.find_by_id(password_id=password_id, user_id=current_user.id)

    if password is None:
        raise PasswordNotFoundError()

    password_repository.delete_by_id(password_id=password_id, user_id=current_user.id)