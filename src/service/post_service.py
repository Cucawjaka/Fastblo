from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.post_schema import BasePost, PostResponse, PostSave
from src.dao.post_dao import PostDAO
from src.errors.data_exeptions import PostNotFoundError
from src.errors.service_exeptions import PermissionDenied


class PostService:
    def __init__(self, session: AsyncSession):
        self._post_dao = PostDAO(session)

    async def create_post(
        self, user_id: int, author: str, post: BasePost
    ) -> PostResponse:
        post_dict = post.model_dump(exclude_unset=True)
        post_dict["user_id"] = user_id
        post_dict["author"] = author
        new_post = PostSave(**post_dict)
        post_from_db = await self._post_dao.add_one_record(values=new_post)
        return PostResponse.model_validate(post_from_db)


    async def get_all_posts(self) -> list[PostResponse]:
        posts_from_db = await self._post_dao.find_all_by_filters()
        if not posts_from_db:
            raise PostNotFoundError(msg="Посты не найдены")
        return [PostResponse.model_validate(post) for post in posts_from_db]


    async def get_post(self, post_id: int) -> PostResponse:
        post_from_db = await self._post_dao.find_one_or_none_by_id(data_id=post_id)
        if not post_from_db:
            raise PostNotFoundError(msg="Пост не найдены")
        return PostResponse.model_validate(post_from_db)


    async def update_post(self, user_id: int, post_id: int, post: BasePost) -> PostResponse:
        post_exists = await self._post_dao.check_existence(data_id=post_id)
        if not post_exists:
            raise PostNotFoundError(msg="Пост не найден")
        post_from_db = await self._post_dao.update_record(values=post, filters={"id": post_id, "user_id": user_id})
        if not post_from_db:
            raise PermissionDenied(msg="Запрещенное действие")
        return PostResponse.model_validate(post_from_db)


    async def delete_post(self, post_id: int, user_id: int) -> None:
        post_exists = await self._post_dao.check_existence(data_id=post_id)
        if not post_exists:
            raise PostNotFoundError(msg="Пост не найден")
        post_deleted = await self._post_dao.delete_records(filters={"id": post_id, "user_id": user_id})
        if post_deleted < 1:
            raise PermissionDenied(msg="Запрещенное действие")
