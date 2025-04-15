from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.dao_dep import get_session_with_commit, get_session_without_commit
from service.post_service import PostService
from service.user_service import UserService


async def get_post_service_with_commmit(
    session: AsyncSession = Depends(get_session_with_commit),
) -> PostService:
    return PostService(session=session)


async def get_post_service_without_commmit(
    session: AsyncSession = Depends(get_session_without_commit),
) -> PostService:
    return PostService(session=session)


async def get_user_service_with_commit(
    session: AsyncSession = Depends(get_session_with_commit),
) -> UserService:
    return UserService(session=session)


async def get_user_service_without_commit(
    session: AsyncSession = Depends(get_session_without_commit),
) -> UserService:
    return UserService(session=session)
