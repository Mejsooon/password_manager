from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import UserCreate, UserLogin, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate):
    try:
        user = auth_service.register_user(user_data)

    except auth_service.UsernameAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    return user


@router.post("/login", response_model=UserResponse)
def login(credentials: UserLogin):
    user = auth_service.authenticate(username=credentials.username, password=credentials.password)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    return user