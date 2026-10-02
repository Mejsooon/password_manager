from pydantic import BaseModel, Field


class PasswordCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    username: str | None = Field(default=None, max_length=255)
    password: str = Field(min_length=1)


class PasswordResponse(BaseModel):
    id: int
    name: str
    username: str | None


class PasswordDetailResponse(BaseModel):
    id: int
    name: str
    username: str | None
    password: str