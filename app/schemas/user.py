from pydantic import BaseModel, EmailStr, Field
from typing import Annotated
from .token import Token


USERNAME_REGEX = r"^[a-zA-Z0-9_]{3,20}$"
PASSWORD_REGEX = r"^[a-zA-Z0-9!@#$%^&*_]{8,}$"

validatedUsername = Annotated[
    str,
    Field(
        pattern=USERNAME_REGEX,
        min_length=3,
        max_length=20,
        description="Username must be 3-20 chars, " +
                    "latin letters, numbers and underscores",
        examples=["valid_user123"]
    )
]
validatedPassword = Annotated[
    str,
    Field(
        pattern=PASSWORD_REGEX,
        min_length=8,
        description="Password must be 8+ chars and can contain " +
                    "latin letters, numbers and special (!@#$%^&*_)",
        examples=["ValidPass!123"]
    )
]


class UserBase(BaseModel):
    email: EmailStr | None = None
    display_name: str | None = None


class UserCredentialsBase(BaseModel):
    username: validatedUsername | None = None
    password: validatedPassword | None = None

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "username": "valid_user123",
                "password": "ValidPass!123",
                "email": "ValidEmail@123",
            }
        }


class UserCreate(UserCredentialsBase, UserBase):
    username: validatedUsername
    password: validatedPassword
    email: EmailStr


class UserUpdate(UserCredentialsBase, UserBase):
    pass


class UserRead(UserBase):
    user_id: int
    username: str
    email: EmailStr
    class Config:
        from_attributes = True


class UserWithToken(BaseModel):
    user: UserRead
    token: Token
