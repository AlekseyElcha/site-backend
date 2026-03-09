from datetime import datetime

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from exeptions import BasicOperationDatabaseError, TokenAlreadyUsed
from src.database.db import get_session
from src.models.models import EmailVerification
from src.schemas.schemas import UserAuthSchema
from src.services.time_service import has_expired


async def validate_auth_user(
        user_data: UserAuthSchema,
        session: AsyncSession = Depends(get_session)
):
    query = (select(EmailVerification).where(EmailVerification.email == user_data.email)
             .where(EmailVerification.code == user_data.auth_code))
    try:
        res = await session.execute(query)
        data = res.scalars().one()
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
        return user_data.email
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Код устарел, запросите новый."
        )
