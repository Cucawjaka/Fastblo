from sqlalchemy.ext.asyncio import AsyncSession

from schemas.user_schema import (
    UserResponse,
    UserWithPosts,
    UserSave,
    UserRegister
)
from db.models import User
from dao.user_dao import UserDAO


class UserService:
    def __init__(self, session: AsyncSession):
        self._user_dao = UserDAO(session)


    async def create_user(self, user: UserRegister) -> UserResponse:
        user_dict = user.model_dump()
        user_dict.pop("confirm_password", None)
        user_dict["is_active"] = True
        new_user = await self._user_dao.add_one_record(values=UserSave(**user_dict))
        return UserResponse.model_validate(new_user)


    async def get_user(self, user_id: int) -> UserResponse:
        user_from_db: User = await self._user_dao.find_one_or_none_by_id(data_id=user_id)
        if user_from_db.is_active:
            return UserResponse.model_validate(user_from_db)
        raise ValueError("Пользователь не найден")
    

    async def get_user_with_posts(self, user_id: int) -> UserWithPosts:
        """Возвращает посты пользователя"""
        user_from_db = await self._user_dao.get_user_with_posts(user_id=user_id)
        if user_from_db.is_active:
            return UserWithPosts.model_validate(user_from_db)
        raise ValueError("Пользователь не найден")


    async def get_all_users(self) -> list[UserResponse]:
        """Возвращает всех пользователей"""
        users_from_db = await self._user_dao.find_all_by_filters(filters={"is_active": True}) 
        return [UserResponse.model_validate(user) for user in users_from_db]


    async def deactive_user(self, user_id: int) -> None:
        """Делает пользователя неактивным"""
        user_deactived, post_deleted = await self._user_dao.deactive_user(user_id)
        if user_deactived > 1:
            raise ValueError("Удалено много пользователей")