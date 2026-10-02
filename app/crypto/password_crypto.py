import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings


def decode_key(key_text: str) -> bytes:
    try:
        key = base64.b64decode(key_text, validate=True)

        if len(key) != 32:
            raise ValueError

        return key

    except Exception as exc:
        raise ValueError("Invalid AES-256 key") from exc


def get_master_key() -> bytes:
    return decode_key(settings.master_key)


def encrypt_password(password: str) -> dict[str, str]:
    key = get_master_key()

    nonce = os.urandom(12)
    aes = AESGCM(key)

    ciphertext = aes.encrypt(
        nonce,
        password.encode("utf-8"),
        None,
    )

    return {
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
    }


def decrypt_password(nonce_text: str, ciphertext_text: str) -> str:
    key = get_master_key()

    try:
        nonce = base64.b64decode(nonce_text, validate=True)
        ciphertext = base64.b64decode(ciphertext_text, validate=True)

        if len(nonce) != 12:
            raise ValueError

    except Exception as exc:
        raise ValueError("Invalid nonce or ciphertext") from exc

    try:
        aes = AESGCM(key)

        plaintext = aes.decrypt(
            nonce,
            ciphertext,
            None,
        )

        return plaintext.decode("utf-8")

    except Exception as exc:
        raise ValueError("Cannot decrypt password") from exc