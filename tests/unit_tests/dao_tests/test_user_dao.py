import pytest

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.db.models import User
from src.dao.user_dao import UserDAO
from src.db.base import async_session_maker
from src.auth.schemas import UserSave
from src.errors.data_exeptions import NotFoundError, Duplicate, TransactionError, IncorrectFilterAppliedError

@pytest.fixture(scope="function")
async def session() -> AsyncSession:
    async with async_session_maker() as s:
        yield s

        await s.close()


@pytest.fixture(scope="function")
def user_dao(session: AsyncSession) -> UserDAO:
    return UserDAO(session=session)


async def test_add_one_record(user_dao: UserDAO) -> None:
    request = UserSave(username="a", email="a@gmail.com", is_active=True, password="vernq0bb4v0qqh")
    response = await user_dao.add_one_record(values=request)
    assert isinstance(response.id, int)

async def test_add_one_record_with_duplicate(user_dao: UserDAO) -> None:
    request = UserSave(username="a", email="a@gmail.com", is_active=True, password="vernq0bb4v0qqh")
    with pytest.raises(Duplicate):
        _ = await user_dao.add_one_record(values=request)
    
# async def test_transaction_error() -> None:
#     with pytest.raises(TransactionError):
#         raise SQLAlchemyError()




async def test_add_many_records(user_dao: UserDAO) -> None:
    ...


async def test_find_one_or_none_by_id(user_dao: UserDAO) -> None:
    ...


async def test_find_one_or_none(user_dao: UserDAO) -> None:
    ...


async def test_find_one_or_none(user_dao: UserDAO) -> None:
    ...


async def test_find_all_by_filters(user_dao: UserDAO) -> None:
    ...


async def test_update_record(user_dao: UserDAO) -> None:
    ...


async def test_delete_records(user_dao: UserDAO) -> None:
    ...


async def test_bulk_update(user_dao: UserDAO):
    ...


async def test_check_existence(user_dao: UserDAO):
    ...


async def test_deactive_user(user_dao: UserDAO) -> None:
    ...


async def test_get_user_with_posts(user_dao: UserDAO) -> None:
    ...