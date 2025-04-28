from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.errors.service_exeptions import PermissionDenied
from src.dependencies.dao_dep import get_session_with_commit
from src.auth.service import AuthService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    payload = AuthService.verify_access_token(token)
    payload["sub"] = int(payload["sub"])
    return payload


def check_owner(user_id: int, current_user: Annotated[dict, Depends(verify_current_user)]) -> None:
    if user_id != current_user["sub"]:
        raise PermissionDenied(msg="Запрещенное действие")
    

def get_refresh_token(request: Request) -> str:
    return request.cookies.get("user_refresh_token")


async def get_auth_service_with_commit(
    session: AsyncSession = Depends(get_session_with_commit),
) -> AuthService:
    return AuthService(session=session)
