from datetime import datetime

from sqlalchemy import func, Integer, TIMESTAMP
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column

from src.config import settings

DATABASE_URL = settings.db_url

engine = create_async_engine(url=DATABASE_URL)

async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    @declared_attr
    @classmethod
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'