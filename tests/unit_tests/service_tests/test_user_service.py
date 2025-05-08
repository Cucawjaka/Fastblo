from unittest.mock import patch, AsyncMock

import pytest, pytest_asyncio

from src.schemas.user_schema import (
    UserResponse,
    UserWithPosts,
    ChangeUsername,
    ChangePassword,
    UserUpdate,
)
from src.schemas.post_schema import PostResponse
from src.errors.service_exeptions import (
    UserInactiveError,
    UserDeletionIntegrityError,
    InvalidCredentialsError,
)
from src.errors.data_exeptions import UserNotFoundError
from src.service.user_service import UserService
from src.db.models import User, Post


@pytest.fixture(scope="function")
def mock_dao():
    with patch("src.service.user_service.UserDAO") as mock_user_dao:
        mock_dao_impl = AsyncMock()
        mock_user_dao.return_value = mock_dao_impl
        yield mock_dao_impl


active_user = User(id=1, is_active=True, username="grisha", email="grishak@gmail.com")
unactive_user = User(id=1, is_active=False)
posts_from_db = [
    Post(id=1, title="a", text="a", user_id=1, author="grisha"),
    Post(id=2, title="a", text="a", user_id=1, author="grisha"),
]
posts = [
    PostResponse(id=1, title="a", text="a", user_id=1, author="grisha"),
    PostResponse(id=2, title="a", text="a", user_id=1, author="grisha"),
]
user_with_posts = User(
    id=1,
    is_active=True,
    username="grisha",
    email="grishak@gmail.com",
    posts=posts_from_db,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mock_return_value, expected_exc",
    [
        (unactive_user, UserInactiveError),
        (None, UserNotFoundError),
        (active_user, None),
    ],
)
async def test_get_user_by_id_with_exceptions(
    mock_dao, mock_return_value, expected_exc
):
    mock_dao.find_one_or_none_by_id.return_value = mock_return_value

    user_service = UserService(session=None)

    if expected_exc:
        with pytest.raises(expected_exc):
            await user_service.get_user_by_id(1)
    else:
        result = await user_service.get_user_by_id(1)
        mock_dao.find_one_or_none_by_id.assert_called_once_with(data_id=1)

        assert isinstance(result, UserResponse)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mock_return_value, posts, expected_exc",
    [
        (unactive_user, None, UserInactiveError),
        (None, None, UserNotFoundError),
        (active_user, list(), None),
        (user_with_posts, posts, None),
    ],
)
async def test_get_user_with_posts(mock_dao, mock_return_value, posts, expected_exc):
    mock_dao.get_user_with_posts.return_value = mock_return_value

    user_service = UserService(session=None)

    if expected_exc:
        with pytest.raises(expected_exc):
            await user_service.get_user_with_posts(1)
    else:
        result = await user_service.get_user_with_posts(1)
        mock_dao.get_user_with_posts.assert_called_once_with(user_id=1)

        assert isinstance(result, UserWithPosts)
        assert result.posts == posts


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mock_return_value, expected_exc",
    [(None, UserNotFoundError), ([active_user, unactive_user], None)],
)
async def test_get_all_users(mock_dao, mock_return_value, expected_exc):
    """Добавить пагинацию"""
    mock_dao.find_all_by_filters.return_value = mock_return_value

    user_service = UserService(session=None)

    if expected_exc:
        with pytest.raises(expected_exc):
            await user_service.get_all_users()
    else:
        result = await user_service.get_all_users()

        assert result == [UserResponse.model_validate(active_user)]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mock_return_value, expected_exc", [(None, UserNotFoundError), (active_user, None)]
)
async def test_update_username(mock_dao, mock_return_value, expected_exc):
    mock_dao.update_record.return_value = mock_return_value
    user_service = UserService(session=None)

    if expected_exc:
        with pytest.raises(expected_exc):
            await user_service.update_username(1, ChangeUsername(username="mishock"))
    else:
        result = await user_service.update_username(
            1, ChangeUsername(username="mishock")
        )
        mock_dao.update_record.assert_called_once_with(
            values=ChangeUsername(username="mishock"),
            filters={"id": 1, "is_active": True},
        )

        assert isinstance(result, UserResponse)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mock_find_func, mock_update_func, expected_exc, mock_verify_func, mock_create_func",
    [
        (None, None, InvalidCredentialsError, False, "hash"),
        (active_user, None, InvalidCredentialsError, False, "hash"),
        (unactive_user, None, InvalidCredentialsError, True, "hash"),
        (active_user, active_user, None, True, "hash"),
    ],
)
async def test_change_password(
    mock_dao,
    mock_find_func,
    mock_update_func,
    expected_exc,
    mock_verify_func,
    mock_create_func,
):
    mock_dao.find_one_or_none_by_id.return_value = mock_find_func
    mock_dao.update_record.return_value = mock_update_func
    user_service = UserService(session=None)

    with patch(
        "src.service.user_service.verify_password",
        side_effect=lambda t, d: mock_verify_func,
    ):
        if expected_exc:
            with pytest.raises(expected_exc):
                await user_service.change_password(
                    1,
                    ChangePassword(
                        password="aaaaaaaa",
                        new_password="1a$aaaaa",
                        confirm_password="1a$aaaaa",
                    ),
                )
        else:
            with patch(
                "src.service.user_service.create_password_hash",
                side_effect=lambda *args, **kwargs: mock_create_func,
            ):
                result = await user_service.change_password(
                    1,
                    ChangePassword(
                        password="aaaaaaaa",
                        new_password="1a$aaaaa",
                        confirm_password="1a$aaaaa",
                    ),
                )

                mock_dao.update_record.assert_called_once_with(
                    values=UserUpdate(password="hash"), filters={"id": 1}
                )

                assert isinstance(result, UserResponse)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mock_return_value, expected_exc",
    [((2, 0), UserDeletionIntegrityError), ((1, 0), None)],
)
async def test_deactive_user(mock_dao, mock_return_value, expected_exc):
    mock_dao.deactive_user.return_value = mock_return_value
    user_service = UserService(session=None)

    if expected_exc:
        with pytest.raises(expected_exc):
            await user_service.deactive_user(1)
    else:
        result = await user_service.deactive_user(1)
        mock_dao.deactive_user.assert_called_once_with(user_id=1)

        assert result is None
