from typing import Annotated, Any

from fastapi import APIRouter, Depends

from dependencies.services_dep import (
    get_user_service_with_commit,
    get_user_service_without_commit,
)
from schemas.user_schema import UserResponse, UserWithPosts, ChangeUsername, ChangePassword
from service.user_service import UserService
from auth.dependencies import verify_current_user, check_owner


router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
async def get_all_users(
    user_service: Annotated[UserService, Depends(get_user_service_without_commit)],
):
    users = await user_service.get_all_users()
    return users


@router.get("/{user_id}/posts", response_model=UserWithPosts)
async def get_user_with_posts(
    user_id: int,
    user_service: Annotated[UserService, Depends(get_user_service_without_commit)],
    _: Annotated[Any, Depends(verify_current_user)],
):
    user = await user_service.get_user_with_posts(user_id=user_id)
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_without_posts(
    user_id: int,
    user_service: Annotated[UserService, Depends(get_user_service_without_commit)],
):
    user = await user_service.get_user(user_id=user_id)
    return user


@router.patch("/{user_id}/username", response_model=UserResponse)
async def change_username(
    user_id: int,
    data: ChangeUsername,
    user_service: Annotated[UserService, Depends(get_user_service_with_commit)],
    _: Annotated[None, Depends(check_owner)]
):
    user = await user_service.update_username(user_id=user_id, data=data)
    return user


@router.patch("/{user_id}/password", response_model=UserResponse)
async def change_password(
    user_id: int,
    data: ChangePassword,
    user_service: Annotated[UserService, Depends(get_user_service_with_commit)],
    _: Annotated[None, Depends(check_owner)]
):
    user = await user_service.change_password(user_id=user_id, data=data)
    return user


@router.patch("/{user_id}/deactivate", response_model=dict)
async def deactivate_user(
    user_id: int,
    user_service: Annotated[UserService, Depends(get_user_service_with_commit)],
    _: Annotated[None, Depends(check_owner)],
):
    await user_service.deactive_user(user_id=user_id)
    return {"message": "Use has been deactivated"}
