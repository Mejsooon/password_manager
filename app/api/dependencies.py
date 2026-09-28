from fastapi import Cookie, HTTPException, status, Request
from app.models.models import User
from app.services import auth_service


def get_current_user(request: Request) -> User:
    session_token = request.cookies.get("session_token")

    if session_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not logged in")

    user = auth_service.get_current_user(session_token)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session Expired")

    return user