from fastapi import APIRouter, Depends

from dependencies.services_dep import get_post_service_with_commmit, get_post_service_without_commmit
from schemas.post_schema import PostResponse, BasePost
from service.post_service import PostService


router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=list[PostResponse])
async def get_all_posts(post_service: PostService = Depends(get_post_service_without_commmit)):
    posts = await post_service.get_all_posts()
    return posts


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, post_service: PostService = Depends(get_post_service_without_commmit)):
    post = await post_service.get_post(post_id=post_id)
    return post


@router.post("", response_model=PostResponse)
async def create_post(user_id: int, author: str, post: BasePost, post_service: PostService = Depends(get_post_service_with_commmit)):
    new_post = await post_service.create_post(user_id=user_id, author=author, post=post)
    return new_post


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post: BasePost, post_service: PostService = Depends(get_post_service_with_commmit)):
    updated_post = await post_service.update_post(post_id=post_id, post=post)
    return updated_post


@router.delete("/{post_id}", response_model=dict)
async def delete_post(post_id: int, post_service: PostService = Depends(get_post_service_with_commmit)):
    await post_service.delete_post(post_id=post_id)
    return {"message": "Post was deleted"}