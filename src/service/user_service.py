from sqlalchemy.ext.asyncio import AsyncSession

from schemas.user_schema import (
    ChangePassword,
    UserResponse,
    UserWithPosts,
    ChangeUsername,
    UserUpdate,
)
from db.models import User
from dao.user_dao import UserDAO
from auth.utils import verify_password, create_password_hash
from errors.service_exeptions import UserInactiveError, InvalidCredentialsError, UserDeletionIntegrityError


class UserService:
    def __init__(self, session: AsyncSession):
        self._user_dao = UserDAO(session)

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        """Возвращает пользователя по id"""
        user_from_db: User = await self._user_dao.find_one_or_none_by_id(
            data_id=user_id
        )
        if user_from_db.is_active:
            return UserResponse.model_validate(user_from_db)
        raise UserInactiveError(msg=f"User is inactive")

    async def get_user_with_posts(self, user_id: int) -> UserWithPosts:
        """Возвращает посты пользователя"""
        user_from_db = await self._user_dao.get_user_with_posts(user_id=user_id)
        if user_from_db.is_active:
            return UserWithPosts.model_validate(user_from_db)
        raise UserInactiveError(msg=f"User is inactive")

    async def get_all_users(self) -> list[UserResponse]:
        """Возвращает всех пользователей"""
        users_from_db = await self._user_dao.find_all_by_filters(
            filters={"is_active": True}
        )
        return [UserResponse.model_validate(user) for user in users_from_db if user.is_active]

    async def update_username(self, user_id: int, data: ChangeUsername) -> UserResponse:
        """Обновляет username пользователя"""
        user_from_db = await self._user_dao.update_record(
            values=data, filters={"id": user_id}
        )
        return UserResponse.model_validate(user_from_db)

    async def change_password(
        self, user_id: int, data: ChangePassword
    ) -> UserResponse:
        """Осуществляет смену пароля"""
        user_from_db = await self._user_dao.find_one_or_none_by_id(data_id=user_id)
        if (
            not verify_password(data.password, user_from_db.password)
            or not user_from_db.is_active
        ):
            raise InvalidCredentialsError(msg="Неверный email или пароль")

        user_from_db = await self._user_dao.update_record(
            values=UserUpdate(
                password=create_password_hash(password=data.new_password)
            ),
            filters={"id": user_id},
        )
        return UserResponse.model_validate(user_from_db)

    async def deactive_user(self, user_id: int) -> None:
        """Делает пользователя неактивным"""
        user_deactived, post_deleted = await self._user_dao.deactive_user(user_id)
        if user_deactived > 1:
            raise UserDeletionIntegrityError(msg="Удалено много пользователей")

