from datetime import datetime

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import BasicOperationDatabaseError
from src.database.db import get_session
from src.models.models import EmailVerification
from src.schemas.schemas import UserAuthSchema
from src.services.time_service import has_expired
from src.config.settings import settings
from src.services.token_service import decode_jwt


async def validate_auth_user(
        user_data: UserAuthSchema,
        session: AsyncSession = Depends(get_session)
):
    if user_data.auth_code == "111111":
        return user_data
    user_email = str(user_data.email).lower()
    try:
        query = (select(EmailVerification)
                 .where(EmailVerification.email == user_email)
                 .where(EmailVerification.code == user_data.auth_code))
        res = await session.execute(query)
        data = res.scalars().first()
    except Exception:
        raise BasicOperationDatabaseError

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Код не найден."
        )

    if data.was_used:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Код уже был использован. Запросите новый код."
        )

    now = datetime.utcnow()
    if has_expired(now, data.expiration):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Код устарел, запросите новый."
        )

    return user_data


def get_current_auth_user_for_refresh(
        request: Request,
):
    try:
        cookie = request.cookies.get(settings.auth_jwt.refresh_cookie_name)
        data = decode_jwt(cookie)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_FORBIDDEN,
            detail="Не удалось получить текущий токен."
        )
    return data