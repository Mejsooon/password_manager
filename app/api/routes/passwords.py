from fastapi import APIRouter, Depends, status, Query

from app.api.dependencies import get_current_user
from app.models.models import User
from app.schemas.password import PasswordCreate, PasswordResponse
from app.services import password_service


router = APIRouter(prefix="/passwords", tags=["Passwords"])


@router.post("", response_model=PasswordResponse, status_code=status.HTTP_201_CREATED)

def create_password(password_data: PasswordCreate, current_user: User = Depends(get_current_user)):

    password = password_service.create_password(current_user=current_user, password_data=password_data,)

    return PasswordResponse(
        id=password.id,
        name=password.name,
        username=password.username,
        password=password_data.password,
    )


@router.get("", response_model=list[PasswordResponse])
def get_passwords(q: str | None = None, limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0), current_user: User = Depends(get_current_user)):
    passwords = password_service.get_passwords(current_user=current_user, search=q, limit=limit, offset=offset)

    return [
        PasswordResponse(
            id=password.id,
            name=password.name,
            username=password.username,
            password=password.ciphertext,
        )
        for password in passwords
    ]


@router.get("/{password_id}", response_model=PasswordResponse)
def get_password(password_id: int, current_user: User = Depends(get_current_user)):

    password = password_service.get_password(current_user=current_user, password_id=password_id,)

    return PasswordResponse(
        id=password.id,
        name=password.name,
        username=password.username,
        password=password.ciphertext,
    )


@router.put("/{password_id}", response_model=PasswordResponse)
def update_password(password_id: int, password_data: PasswordCreate, current_user: User = Depends(get_current_user)):

    password = password_service.update_password(current_user=current_user, password_id=password_id, password_data=password_data,)

    return PasswordResponse(id=password.id, name=password.name, username=password.username, password=password_data.password,)


@router.delete("/{password_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_password(password_id: int, current_user: User = Depends(get_current_user)):

        password_service.delete_password(current_user=current_user, password_id=password_id)
