from fastapi import APIRouter, Depends

from dependencies.services_dep import get_user_service_with_commit, get_user_service_without_commit
from schemas.user_schema import UserResponse, UserWithPosts, UserRegister
from service.user_service import UserService


router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
async def get_all_users(user_service: UserService = Depends(get_user_service_without_commit)):
    users = await user_service.get_all_users()
    return users


@router.get("/{user_id}/posts", response_model=UserWithPosts)
async def get_user_with_posts(user_id: int, user_service: UserService = Depends(get_user_service_without_commit)):
    user = await user_service.get_user_with_posts(user_id=user_id)
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_without_posts(user_id: int, user_service: UserService = Depends(get_user_service_without_commit)):
    user  = await user_service.get_user(user_id=user_id)
    return user


@router.post("", response_model=UserResponse)
async def register_user(user: UserRegister, user_service: UserService = Depends(get_user_service_with_commit)):
    new_user = await user_service.create_user(user)
    return new_user


@router.patch("/{user_id}/deactivate", response_model=dict)
async def deactivate_user(user_id: int, user_service: UserService = Depends(get_user_service_with_commit)):
    await user_service.deactive_user(user_id=user_id)
    return {"message": "Use has been deactivated"}