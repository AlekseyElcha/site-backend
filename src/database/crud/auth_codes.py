from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from exeptions import (
    AddNewEmailVerificationCodeToDBError,
    BasicOperationDatabaseError,
)
from src.models.models import EmailVerification
from src.schemas.schemas import NewEmailVerificationCode


async def add_auth_code_to_db(
        code: NewEmailVerificationCode,
        session: AsyncSession,
):
    new_code = EmailVerification(**code.model_dump())
    session.add(new_code)
    try:
        await session.commit()
        await session.refresh(new_code)
    except:
        raise AddNewEmailVerificationCodeToDBError
    return True


async def change_auth_code_usage_status_by_user_email(email: str, used: bool, session: AsyncSession):
    query = update(EmailVerification).where(EmailVerification.email == email).values(was_used=used)
    try:
        await session.execute(query)
        await session.commit()
    except:
        raise BasicOperationDatabaseError
