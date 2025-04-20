from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import exists, select

from db.base_dao import BaseDAO
from db.models import Post


class PostDAO(BaseDAO):
    model = Post

    async def check_existence(self, post_id: int) -> bool:
        try:
            stmt = select(exists().where(self.model.id == post_id))
            result = await self._session.execute(stmt)
            return result.scalar()
        except SQLAlchemyError as e:
            raise

    