from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_user
from app.models.models import User
from app.schemas.password import (
    PasswordCreate,
    PasswordDetailResponse,
    PasswordResponse,
)
from app.services import password_service


router = APIRouter(
    prefix="/passwords",
    tags=["Passwords"],
)


@router.post(
    "",
    response_model=PasswordDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_password(
    password_data: PasswordCreate,
    current_user: User = Depends(get_current_user),
):
    password = password_service.create_password(
        current_user=current_user,
        password_data=password_data,
    )

    return PasswordDetailResponse(
        id=password.id,
        name=password.name,
        username=password.username,
        password=password_data.password,
    )


@router.get(
    "",
    response_model=list[PasswordResponse],
)
def get_passwords(
    current_user: User = Depends(get_current_user),
):
    passwords = password_service.get_passwords(
        current_user=current_user,
    )

    return [
        PasswordResponse(
            id=password.id,
            name=password.name,
            username=password.username,
        )
        for password in passwords
    ]


@router.get(
    "/{password_id}",
    response_model=PasswordDetailResponse,
)
def get_password(
    password_id: int,
    current_user: User = Depends(get_current_user),
):
    password = password_service.get_password(
        current_user=current_user,
        password_id=password_id,
    )

    return PasswordDetailResponse(
        id=password.id,
        name=password.name,
        username=password.username,
        password=password.password,
    )


@router.put(
    "/{password_id}",
    response_model=PasswordDetailResponse,
)
def update_password(
    password_id: int,
    password_data: PasswordCreate,
    current_user: User = Depends(get_current_user),
):
    password = password_service.update_password(
        current_user=current_user,
        password_id=password_id,
        password_data=password_data,
    )

    return PasswordDetailResponse(
        id=password.id,
        name=password.name,
        username=password.username,
        password=password_data.password,
    )