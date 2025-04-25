from typing import Self
import re

from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator, model_validator

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


class ChangeUsername(BaseModel):
    username: str = Field(...)


class ChangePassword(BaseModel):
    password: str = Field(..., min_length=8, max_length=50, exclude=True)
    new_password: str = Field(default=..., min_length=8, max_length=50)
    confirm_password: str = Field(default=..., min_length=8, max_length=50, exclude=True)


    @field_validator("new_password", mode="before")
    @classmethod
    def validate_password(cls, value) -> str:
        if re.search(r"(?=.*\d)(?=.*\W)(?=.*[a-zA-Z])", value) is None:
            raise Val(
                "Пароль должен содержать хотя бы одну цифру и специальный символ"
            )
        return value
    
    
    @model_validator(mode="after")
    def check_password(self) -> Self:
        if self.new_password != self.confirm_password:
            raise  ValueError('Пароли не совпадают')
        return self
    

class UserUpdate(BaseModel):
    password: str = Field(...)