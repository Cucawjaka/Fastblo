from typing import Self
import re

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from schemas.user_schema import BaseUser

class UserLogin(BaseModel):  # вход
    email: EmailStr = Field(...)
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


class ChangePassword(BaseModel):
    password: str = Field(..., min_length=8, max_length=50, exclude=True)
    new_password: str = Field(default=..., min_length=8, max_length=50)
    confirm_password: str = Field(default=..., min_length=8, max_length=50, exclude=True)


    @field_validator("new_password", mode="before")
    @classmethod
    def validate_password(cls, value) -> str:
        if re.search(r"(?=.*\d)(?=.*\W)(?=.*[a-zA-Z])", value) is None:
            raise ValueError(
                "Пароль должен содержать хотя бы одну цифру и специальный символ"
            )
        return value
    
    
    @model_validator(mode="after")
    def check_password(self) -> Self:
        if self.new_password != self.confirm_password:
            raise  ValueError('Пароли не совпадают')
        return self


class UserSave(BaseUser):
    is_active: bool = Field(default=...)
    password: str = Field(default=...)

class UserUpdate(BaseModel):
    password: str = Field(...)

class TokenResponse(BaseModel):
    access_token: str = Field(...)
    token_type: str = Field(default="bearer")


class RefreshTokenSave(BaseModel):
    refresh_token: str = Field(...)
    user_id: int = Field(...)
