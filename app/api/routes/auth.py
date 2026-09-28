from fastapi import APIRouter, HTTPException, status, Response, Request
from app.schemas.auth import UserCreate, UserLogin, UserResponse
from app.services import auth_service


router = APIRouter(prefix="/auth", tags=["Authentication"])

SESSION_COOKIE_NAME = "session_token"
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 7 dni


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate):
    try:
        user = auth_service.register_user(user_data)

    except auth_service.UsernameAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    return user


@router.post("/login", response_model=UserResponse)
def login(credentials: UserLogin, response: Response):
    user = auth_service.authenticate(username=credentials.username, password=credentials.password)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    session_token = auth_service.create_session(user.id)

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="Lax",
        secure=False,
        path="/",
    )

    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, request: Request):

    session_token=request.cookies.get(SESSION_COOKIE_NAME)

    if session_token is not None:
        auth_service.logout(session_token)

    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")