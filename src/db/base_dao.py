from typing import Generic, TypeVar

from asyncpg.exceptions import UniqueViolationError
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import select, update, delete, insert, exists

from db.base import Base
from errors.data_exeptions import NotFoundError, Duplicate, TransactionError

T = TypeVar("T", bound=Base)


class BaseDAO(Generic[T]):
    model: type[T] = None

    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session
        if self.model is None:
            raise ValueError("Модель должна быть указана")

    async def find_one_or_none_by_id(self, data_id: int) -> T:
        try:
            stmt = select(self.model).filter_by(id=data_id)
            result = await self._session.execute(stmt)
            record = result.scalar_one_or_none()
            if record is None:
                raise NotFoundError(msg=f"{self.model.__name__} not found ")
            return record
        except SQLAlchemyError as e:
            raise TransactionError()


    async def find_one_or_none(self, filters: dict = {}) -> T:
        try:
            stmt = select(self.model).filter_by(**filters)
            result = await self._session.execute(stmt)
            record = result.scalar_one_or_none()
            if record is None:
                raise NotFoundError(msg=f"{self.model.__name__} not found ")
            return record
        except SQLAlchemyError as e:
            raise TransactionError()


    async def find_all_by_filters(self, filters: dict = {}) -> list[T]:
        try:
            stmt = select(self.model).filter_by(**filters)
            result = await self._session.execute(stmt)
            records = result.scalars().all()
            if records is None:
                raise NotFoundError(msg=f"{self.model.__name__} not found ")
            return records
        except SQLAlchemyError as e:
            raise TransactionError()


    async def add_one_record(self, values: BaseModel) -> T:
        values_dict = values.model_dump(exclude_unset=True)
        try:
            stmt = insert(self.model).values(values_dict)
            result = await self._session.execute(stmt.returning(self.model))
            record = result.scalar_one_or_none()
            return record
        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolationError):
                raise Duplicate(msg=f"{self.model.__name__} already exists")
        except SQLAlchemyError as e:
            raise TransactionError()


    async def add_many_records(self, values_list: list[BaseModel]) -> list[T]:
        values_dict_list = [
            values.model_dump(exclude_unset=True) for values in values_list
        ]
        try:
            stmt = insert(self.model).values(values_dict_list)
            result = await self._session.execute(stmt.returning(self.model))
            records = result.scalars().all()
            return records
        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolationError):
                raise Duplicate(msg=f"{self.model.__name__} already exists")
        except SQLAlchemyError as e:
            raise TransactionError()


    async def update_record(self, values: BaseModel, filters: dict = {}) -> T:
        values_dict = values.model_dump(exclude_unset=True)
        try:
            stmt = (
                update(self.model)
                .where(*[getattr(self.model, k) == v for k, v in filters.items()])
                .values(**values_dict)
                .returning(self.model)
            )
            result = await self._session.execute(stmt)
            await self._session.flush()
            record = result.scalar_one_or_none()
            if record is None:
                raise NotFoundError(msg=f"{self.model.__name__} not found ")
            return record
        except SQLAlchemyError as e:
            raise TransactionError() 


    async def bulk_update(self, records: list[BaseModel]) -> int:
        try:
            updated_count = 0
            for record in records:
                record_dict = record.model_dump(exclude_unset=True)
                if "id" not in record_dict:
                    continue

                update_data = {k: v for k, v in record_dict.items() if k != "id"}
                stmt = (
                    update(self.model)
                    .where(self.model.id == record_dict)
                    .values(**update_data)
                )
                result = await self._session.execute(stmt)
                updated_count += result.rowcount
                await self._session.flush()
                return updated_count
        except SQLAlchemyError as e:
            raise TransactionError() 


    async def delete_records(self, filters: dict = {}) -> int:
        try:
            stmt = delete(self.model).where(
                *[getattr(self.model, k) == v for k, v in filters.items()]
            )
            result = await self._session.execute(stmt)
            await self._session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            raise TransactionError()

    
    async def check_existence(self, data_id: int) -> bool:
            try:
                stmt = select(exists().where(self.model.id == data_id))
                result = await self._session.execute(stmt)
                return result.scalar()
            except SQLAlchemyError as e:
                raise TransactionError()