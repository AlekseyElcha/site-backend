from typing import Annotated
import logging
from fastapi import APIRouter, Form, HTTPException, status, Depends, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import BasicOperationDatabaseError, SendEmailError
from src.auth.code_generator import generate_auth_code_and_and_to_db
from src.auth.utils import validate_auth_user, get_current_auth_user_for_refresh
from src.config.settings import settings
from src.database.crud.auth_codes import (
    change_auth_code_usage_status_by_user_email,
)
from src.database.crud.users import get_user_role_if_user_exists_else_create_new_user
from src.database.db import get_session
from src.schemas.schemas import UserAuthSchema
from src.services.email_service import send_auth_code
from src.services.token_service import (
    create_access_token,
    decode_jwt, create_refresh_token,
)

logging.basicConfig(
    level=settings.logs.level,
    datefmt=settings.logs.datefmt,
    format=settings.logs.format,
)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/get_auth_code")
async def get_auth_code(session: Annotated[AsyncSession, Depends(get_session)], email: str = Form()):
    code = await generate_auth_code_and_and_to_db(email=email.lower(), session=session)
    try:
        await send_auth_code(user_email=email.lower(), auth_code=code)
    except SendEmailError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла ошибка при отправке email с кодом для входа. Повторите попытку позже."
        )
    return code


@router.post("/login")
async def login(
    response: Response,
    user_data: UserAuthSchema = Depends(validate_auth_user),
    session: AsyncSession = Depends(get_session),
):
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    user_role = await get_user_role_if_user_exists_else_create_new_user(
        user_email=user_data.email.lower(),
        session=session
    )
    try:
        await change_auth_code_usage_status_by_user_email(
            user_data=user_data,
            used=True,
            session=session,
        )
    except BasicOperationDatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла ошибка сервера.",
        )
    access_token = create_access_token(user_data.email, user_role)
    refresh_token = create_refresh_token(user_data.email, user_role)

    # TODO добавить параметры работы (httponly, samesite, secure)
    response.set_cookie(
        key=settings.auth_jwt.access_cookie_name,
        value=access_token,
    )
    response.set_cookie(
        key=settings.auth_jwt.refresh_cookie_name,
        value=refresh_token
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

# TODO добавить проверку валидности (время истечения) для refresh токена
@router.post("/refresh")
def refresh(
        response: Response,
        request: Request,
        user_data = Depends(get_current_auth_user_for_refresh)
    ):
        access_token = create_access_token(user_data.get("sub"), user_data.get("role"))
        response.delete_cookie(settings.auth_jwt.access_cookie_name)
        response.set_cookie(
            key=settings.auth_jwt.access_cookie_name,
            value=access_token
        )
        return {
            "access_token": access_token,
        }


@router.get("/user_info")
def auth_user_check_self_info(
        request: Request,
):
    try:
        cookie = request.cookies.get(settings.auth_jwt.access_cookie_name)
        data = decode_jwt(cookie)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы."
        )
    return data


@router.get("/logout")
async def logout(request: Request, response: Response):
    response.delete_cookie(key=settings.auth_jwt.access_cookie_name)
    return {
        "message": "Вы вышли из системы."
    }
