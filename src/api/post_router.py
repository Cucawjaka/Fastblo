from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from dependencies.services_dep import (
    get_post_service_with_commmit,
    get_post_service_without_commmit,
)
from schemas.post_schema import PostResponse, BasePost
from service.post_service import PostService
from auth.dependencies import verify_current_user
from errors.service_exeptions import PermissionDenied


router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=list[PostResponse])
async def get_all_posts(
    post_service: Annotated[PostService, Depends(get_post_service_without_commmit)],
):
    posts = await post_service.get_all_posts()
    return posts


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    post_service: Annotated[PostService, Depends(get_post_service_without_commmit)],
):
    post = await post_service.get_post(post_id=post_id)
    return post


@router.post("", response_model=PostResponse, status_code=201)
async def create_post(
    post: BasePost,
    post_service: Annotated[PostService, Depends(get_post_service_with_commmit)],
    payload: Annotated[dict, Depends(verify_current_user)],
):
    new_post = await post_service.create_post(user_id=payload["sub"], author=payload["username"], post=post)
    return new_post


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post: BasePost,
    post_service: Annotated[PostService, Depends(get_post_service_with_commmit)],
    payload: Annotated[dict, Depends(verify_current_user)],
):
    updated_post = await post_service.update_post(user_id=payload["sub"], post_id=post_id, post=post)
    return updated_post


@router.delete("/{post_id}", response_model=dict)
async def delete_post(
    post_id: int,
    post_service: Annotated[PostService, Depends(get_post_service_with_commmit)],
    payload: Annotated[dict, Depends(verify_current_user)],
):
    await post_service.delete_post(post_id=post_id, user_id=payload["sub"])
    return {"message": "Post was deleted"}
    
