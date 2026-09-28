from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: int | None
    username: str
    password_hash: str
    created_at: datetime | None = None


@dataclass
class Session:
    id: int | None
    user_id: int
    token_hash: str
    expires_at: datetime
    created_at: datetime | None = None


@dataclass
class Password:
    id: int | None
    user_id: int
    name: str
    username: str | None
    nonce: str
    ciphertext: str
    created_at: datetime | None = None