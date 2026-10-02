from fastapi import Request

from app.core.exceptions import SessionInvalidError
from app.models.models import User
from app.services import auth_service


SESSION_COOKIE_NAME = "session_token"


def get_current_user(request: Request) -> User:
    session_token = request.cookies.get(SESSION_COOKIE_NAME)

    if session_token is None:
        raise SessionInvalidError()

    return auth_service.get_current_user(session_token)