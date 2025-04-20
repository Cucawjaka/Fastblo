from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey

from db.base import Base


class Token(Base):
    refresh_token: Mapped[str] = mapped_column(String, unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
