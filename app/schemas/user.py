from pydantic import BaseModel, EmailStr
from .token import Token


class UserBase(BaseModel):
    username: str
    display_name: str | None = None
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    user_id: int
    class Config:
        from_attributes = True


class UserUpdate(UserBase):
    password: str


class UserWithToken(BaseModel):
    user: UserRead
    token: Token
