from fastapi import Cookie, HTTPException, status, Request
from app.models.models import User
from app.services import auth_service
from app.core.exceptions import SessionInvalidError


def get_current_user(request: Request) -> User:
    session_token = request.cookies.get("session_token")

    if session_token is None:
        raise SessionInvalidError()

    user = auth_service.get_current_user(session_token)

    if user is None:
        raise SessionInvalidError()

    return user