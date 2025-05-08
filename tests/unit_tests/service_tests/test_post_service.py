from unittest.mock import patch, AsyncMock

import pytest, pytest_asyncio

from src.schemas.post_schema import BasePost, PostResponse, PostSave
from src.errors.service_exeptions import PermissionDenied
from src.errors.data_exeptions import PostNotFoundError
from src.service.post_service import PostService
from src.db.models import Post


@patch("src.service.post_service.PostDAO")
@pytest.mark.asyncio
async def test_create_post(mock_post_dao):
    mock_dao = AsyncMock()
    mock_dao.add_one_record.return_value = Post(
        id=1, user_id=1, title="a", text="a", author="grisha"
    )
    mock_post_dao.return_value = mock_dao

    post_service = PostService(session=None)

    result = await post_service.create_post(
        user_id=1, author="grisha", post=BasePost(title="a", text="a")
    )

    expected_post_save = PostSave(title="a", text="a", user_id=1, author="grisha")
    mock_dao.add_one_record.assert_called_once_with(values=expected_post_save)

    assert result.user_id == 1
    assert result.author == "grisha"


# @patch("src.service.post_service.PostDAO")
# @pytest.mark.asyncio
#     "после добавления пагинации"


@patch("src.service.post_service.PostDAO")
@pytest.mark.asyncio
async def test_get_all_posts_with_exception(mock_post_dao):
    mock_dao = AsyncMock()
    mock_dao.find_all_by_filters.side_effect = PostNotFoundError()
    mock_post_dao.return_value = mock_dao

    post_service = PostService(session=None)

    with pytest.raises(PostNotFoundError):
        await post_service.get_all_posts()


@patch("src.service.post_service.PostDAO")
@pytest.mark.asyncio
async def test_get_post_with_exception(mock_post_dao):
    mock_dao = AsyncMock()
    mock_dao.find_one_or_none_by_id.return_value = None
    mock_post_dao.return_value = mock_dao

    post_service = PostService(session=None)

    with pytest.raises(PostNotFoundError):
        await post_service.get_post(post_id=1)


@patch("src.service.post_service.PostDAO")
@pytest.mark.asyncio
async def test_update_post(mock_post_dao):
    mock_dao = AsyncMock()
    mock_dao.check_exictence.return_value = True
    mock_dao.update_record.return_value = Post(
        id=1, user_id=1, title="b", text="b", author="grisha"
    )

    mock_post_dao.return_value = mock_dao
    post_service = PostService(session=None)

    new_post = BasePost(title="b", text="b")
    result = await post_service.update_post(1, 1, post=new_post)
    mock_dao.update_record.assert_called_once_with(
        values=new_post, filters={"id": 1, "user_id": 1}
    )

    assert result.title == "b"


@patch("src.service.post_service.PostDAO")
@pytest.mark.asyncio
async def test_update_post_with_not_found_error(mock_post_dao):
    mock_dao = AsyncMock()
    mock_dao.check_existence.return_value = False

    mock_post_dao.return_value = mock_dao
    post_service = PostService(session=None)

    with pytest.raises(PostNotFoundError):
        await post_service.update_post(1, 1, BasePost(title="a", text="a"))


@patch("src.service.post_service.PostDAO")
@pytest.mark.asyncio
async def test_update_post_with_permission_error(mock_post_dao):
    mock_dao = AsyncMock()
    mock_dao.check_existence.return_value = True
    mock_dao.update_record.return_value = None

    mock_post_dao.return_value = mock_dao
    post_service = PostService(session=None)

    with pytest.raises(PermissionDenied):
        await post_service.update_post(1, 1, BasePost(title="a", text="a"))


@patch("src.service.post_service.PostDAO")
@pytest.mark.asyncio
async def test_delete_post_with_not_found_error(mock_post_dao):
    mock_dao = AsyncMock()
    mock_dao.check_existence.return_value = False

    mock_post_dao.return_value = mock_dao
    post_service = PostService(session=None)

    with pytest.raises(PostNotFoundError):
        await post_service.delete_post(1, 1)


@patch("src.service.post_service.PostDAO")
@pytest.mark.asyncio
async def test_delete_post_with_permission_error(mock_post_dao):
    mock_dao = AsyncMock()
    mock_dao.check_existence.return_value = True
    mock_dao.delete_records.return_value = 0

    mock_post_dao.return_value = mock_dao
    post_service = PostService(session=None)

    with pytest.raises(PermissionDenied):
        await post_service.delete_post(1, 1)
