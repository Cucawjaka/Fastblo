from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import Response

from src.auth.dependencies import get_auth_service_with_commit, verify_current_user, get_refresh_token
from src.auth.schemas import UserRegister, UserLogin, TokenResponse
from src.auth.service import AuthService


router = APIRouter(prefix="/auth", tags=["User Auth"])


def set_refresh_cookie(response: Response, token: str):
    response.set_cookie(
        key="user_refresh_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
    )


@router.post("/register", response_model=TokenResponse)
async def register(
    user: UserRegister,
    auth_service: Annotated[AuthService, Depends(get_auth_service_with_commit)],
    response: Response,
):
    tokens = await auth_service.register_user(user)
    set_refresh_cookie(response, tokens["refresh_token"])

    return TokenResponse(access_token=tokens["access_token"])


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service_with_commit)],
    response: Response,
):
    user_login = UserLogin(email=form_data.username, password=form_data.password)
    tokens = await auth_service.login_user(user=user_login)
    set_refresh_cookie(response, tokens["refresh_token"])

    return TokenResponse(access_token=tokens["access_token"])


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    token: Annotated[str, Depends(get_refresh_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service_with_commit)],
    response: Response,
):
    tokens = await auth_service.refresh_tokens(refresh_token=token)
    set_refresh_cookie(response, tokens["refresh_token"])

    return TokenResponse(access_token=tokens["access_token"])


@router.post("/logout")
async def logout(
    payload: Annotated[dict, Depends(verify_current_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service_with_commit)],
    response: Response,
):
    response.delete_cookie("user_refresh_token")
    await auth_service.logout_user_from_this_device(user_id=payload["sub"])


