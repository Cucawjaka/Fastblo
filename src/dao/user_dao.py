from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlalchemy import update, delete, select

from db.base_dao import BaseDAO
from db.models import User, Post


class UserDAO(BaseDAO):
    model = User

    async def deactive_user(self, user_id: int) -> tuple[int, int]:
        try:
            stmt_1 = update(self.model).where(self.model.id == user_id).values(is_active = False)
            result_user_deactive = await self._session.execute(stmt_1)
            stmt_2 = delete(Post).where(Post.user_id == user_id)
            result_post_delete = await self._session.execute(stmt_2)
            await self._session.flush()
            return result_user_deactive.rowcount, result_post_delete.rowcount
        except SQLAlchemyError as e:
            raise  


    async def get_user_with_posts(self, user_id: int) -> User:
        try:
            stmt = select(self.model).options(selectinload(self.model.posts)).where(self.model.id == user_id)
            result = await self._session.execute(stmt)
            record = result.scalar_one_or_none()
            return record
        except SQLAlchemyError as e:
            raise
        