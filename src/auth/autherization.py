from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, status, Depends, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession

from exeptions import BasicOperationDatabaseError
from src.auth.code_generator import generate_auth_code_and_and_to_db
from src.auth.utils import validate_auth_user
from src.config.settings import settings
from src.database.crud.auth_codes import (
    change_auth_code_usage_status_by_user_email,
)
from src.database.crud.users import get_user_role_if_user_exists_else_create_new_user
from src.database.db import get_session
from src.schemas.schemas import TokenInfo
from src.services.token_service import (
    create_access_token,
    decode_jwt,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/get_auth_code")
async def get_auth_code(session: Annotated[AsyncSession, Depends(get_session)], email: str = Form()):
    code = await generate_auth_code_and_and_to_db(email=email, session=session)
    return code


@router.post("/login")
async def login(
    response: Response,
    user_email: str = Depends(validate_auth_user),
    session: AsyncSession = Depends(get_session),
):
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    user_role = await get_user_role_if_user_exists_else_create_new_user(user_email=user_email, session=session)
    try:
        await change_auth_code_usage_status_by_user_email(email=user_email, used=True, session=session)
    except BasicOperationDatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла ошибка сервера.",
        )
    access_token = create_access_token(user_email, user_role)
    response.set_cookie(
        key=settings.auth_jwt.access_cookie_name,
        value=access_token,
    )

    return {"access_token": access_token}

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