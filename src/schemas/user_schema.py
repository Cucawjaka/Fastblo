import re
from typing import Self

from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator, ConfigDict

from schemas.post_schema import PostResponse


class BaseUser(BaseModel):
    username: str = Field(default=..., max_length=50, pattern=r"^\w+$")
    email: EmailStr = Field(default=..., max_length=70)

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseUser):
    id: int = Field(...)
    is_active: bool = Field(...)
    # is_admin: bool = Field(...)


class UserWithPosts(UserResponse):
    posts: list[PostResponse] = Field(default_factory=list)


class UserLogin(BaseModel):  # вход
    email: EmailStr = Field(default=None)
    password: str = Field(default=..., min_length=8, max_length=50)


class UserRegister(BaseUser):  # регистрация
    password: str = Field(default=..., min_length=8, max_length=50)
    confirm_password: str = Field(default=..., min_length=8, max_length=50, exclude=True)

    @field_validator("password", mode="before")
    @classmethod
    def validate_password(cls, value) -> str:
        if re.search(r"(?=.*\d)(?=.*\W)(?=.*[a-zA-Z])", value) is None:
            raise ValueError(
                "Пароль должен содержать хотя бы одну цифру и специальный символ"
            )
        return value
    
    @field_validator("username", mode="before")
    @classmethod
    def check_username(cls, value) -> str: 
        value = value.strip()
        if " " in value:
            raise ValueError("Имя пользователя не должно содержать пробелов")
        return value
    
    @model_validator(mode="after")
    def check_password(self) -> Self:
        if self.password != self.confirm_password:
            raise  ValueError('Пароли не совпадают')
        return self


class UserSave(BaseUser):
    is_active: bool = Field(default=...)
    password: str = Field(default=..., min_length=8, max_length=50)