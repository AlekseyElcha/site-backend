from datetime import datetime

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from exeptions import BasicOperationDatabaseError, TokenAlreadyUsed
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
    # TODO только для разработки!!!
    if user_data.auth_code == "111111":
        return user_data
    query = (select(EmailVerification).where(EmailVerification.email == user_data.email)
             .where(EmailVerification.code == user_data.auth_code))
    try:
        res = await session.execute(query)
        data = res.scalars().first()
    except:
        raise BasicOperationDatabaseError
    if data.was_used:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Код уже был использован. Запросите новый код."
        )
    now = datetime.utcnow()
    exp = data.expiration
    has_exp = has_expired(now, exp)
    if not has_exp:
        return user_data
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Код устарел, запросите новый."
        )



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