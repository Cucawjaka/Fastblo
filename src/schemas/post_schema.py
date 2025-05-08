from pydantic import BaseModel, ConfigDict, Field


class BasePost(BaseModel):
    title: str = Field(..., min_length=1, max_length=40)
    text: str = Field(..., min_length=1)

    model_config = ConfigDict(from_attributes=True)


class PostSave(BasePost):
    user_id: int = Field(...)
    author: str = Field(...)


class PostResponse(PostSave):
    id: int = Field(...)
    

