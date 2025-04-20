from sqlalchemy.ext.asyncio import AsyncSession

from schemas.post_schema import BasePost, PostResponse, PostSave
from dao.post_dao import PostDAO


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
        return [PostResponse.model_validate(post) for post in posts_from_db]


    async def get_post(self, post_id: int) -> PostResponse:
        post_from_db = await self._post_dao.find_one_or_none_by_id(data_id=post_id)
        return PostResponse.model_validate(post_from_db)


    async def update_post(self, user_id: int, post_id: int, post: BasePost) -> PostResponse:
        post_exists = await self._post_dao.check_existence(post_id=post_id)
        if not post_exists:
            raise ValueError("Пост не найден")
        post_from_db = await self._post_dao.update_record(values=post, filters={"id": post_id, "user_id": user_id})
        if not post_from_db:
            raise ValueError("Запрещенное действие")
        return PostResponse.model_validate(post_from_db)


    async def delete_post(self, post_id: int, user_id: int) -> None:
        post_exists = await self._post_dao.check_existence(post_id=post_id)
        if not post_exists:
            raise ValueError("Пост не найден")
        post_deleted = await self._post_dao.delete_records(filters={"id": post_id, "user_id": user_id})
        if post_deleted < 1:
            raise ValueError("Запрещенное действие")
