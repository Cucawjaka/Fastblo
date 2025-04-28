from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    ForeignKey,
    String,
    Boolean,
    Text,
    text,
)

from src.db.base import Base

class User(Base):
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(70), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"))
    # is_admin: Mapped[bool] = mapped_column(Boolean, server_default=text("FALSE"))
    password: Mapped[str]

    posts: Mapped[list["Post"]] = relationship(
        "Post",
        back_populates="user",
        cascade="save-update, merge, delete, delete-orphan",
        lazy=True,
    )


class Post(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str]
    text: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String) 

    user: Mapped["User"] = relationship("User", back_populates="posts", uselist=False)

