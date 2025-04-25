from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from dao.user_dao import UserDAO
from errors.service_exeptions import InvalidCredentialsError, InvalidTokenTypeError, TokenRefreshError
from errors.data_exeptions import UserNotFoundError
from .utils import (
    create_password_hash,
    verify_password,
    verify_token,
    create_refresh_and_access_tokens
)
from .schemas import (
    UserLogin,
    UserRegister,
    UserSave,
    RefreshTokenSave,
)
from .dao import TokenDAO


class AuthService:
    def __init__(self, session: AsyncSession):
        self._user_dao = UserDAO(session)
        self._token_dao = TokenDAO(session)

    async def register_user(self, user: UserRegister) -> dict[str, str]:
        """Регистрация пользователя"""
        user_dict = user.model_dump()
        user_dict["is_active"] = True
        user_dict["password"] = create_password_hash(password=user.password)
        new_user: User = await self._user_dao.add_one_record(
            values=UserSave(**user_dict)
        )

        tokens_dict = create_refresh_and_access_tokens(
            user_id=new_user.id, username=new_user.username
        )

        await self._token_dao.add_one_record(
            values=RefreshTokenSave(
                refresh_token=tokens_dict["refresh_token"],
                user_id=new_user.id
            )
        )
        return tokens_dict

    async def login_user(self, user: UserLogin) -> dict[str, str]:
        """Вход пользователя в систему"""
        user_from_db = await self._user_dao.find_one_or_none(filters={"email": user.email})
        if not user_from_db or not verify_password(user.password, user_from_db.password) or not user_from_db.is_active:
            raise InvalidCredentialsError(msg="Неверный email или пароль")

        tokens_dict = create_refresh_and_access_tokens(
            user_id=user_from_db.id, username=user_from_db.username
        )

        await self._token_dao.delete_records(filters={"user_id": user_from_db.id})
        await self._token_dao.add_one_record(
            values=RefreshTokenSave(
                refresh_token=tokens_dict["refresh_token"],
                user_id=user_from_db.id
            )
        )
        return tokens_dict

    
    async def refresh_tokens(self, refresh_token) -> dict[str, str]:
        """Обновляет access и refresh токены"""
        user_info = verify_token(refresh_token)
        if user_info.get("token_type") != "refresh":
            raise InvalidTokenTypeError("Неверный тип токена")
        
        user_from_db = await self._user_dao.find_one_or_none_by_id(data_id=int(user_info["sub"]))
        if  not user_from_db.is_active:
            raise UserNotFoundError(msg="Такого пользователя не существует")

        new_tokens_dict = create_refresh_and_access_tokens(
            user_id=user_from_db.id, username=user_from_db.username
        )

        token_from_db = await self._token_dao.update_record(
            values=RefreshTokenSave(
                refresh_token=new_tokens_dict["refresh_token"],
                user_id=user_from_db.id
            ),
            filters={"user_id": user_from_db.id}
        )
        if not token_from_db:
            raise TokenRefreshError(msg="Обновление токенов невозможно")
        return new_tokens_dict
    
    async def logout_user_from_this_device(self, user_id: int) -> None:
        """Выход пользователя с этого устройства"""
        await self._token_dao.delete_records(filters={"user_id": user_id})

    @staticmethod
    def verify_access_token(token: str) -> dict:
        payload = verify_token(token)
        if payload.get("token_type") != "access":
            raise InvalidTokenTypeError(msg="Неверный тип токена")
        return payload