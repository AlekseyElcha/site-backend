from random import choice
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import (
    CreateNewEmailVerificationCodeError,
    AddNewEmailVerificationCodeToDBError,
)
from src.config.settings import settings
from src.database.crud.auth_codes import add_auth_code_to_db
from src.schemas.schemas import NewEmailVerificationCode

nums = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
mins = settings.business.email_code_verification_timeout_minutes

async def generate_auth_code_and_and_to_db(email: str, session: AsyncSession):
    now_unix_str = str(datetime.timestamp(datetime.utcnow()))
    first_part = "".join(choice(nums) for i in range(3))
    second_part = now_unix_str[-3:]
    code = first_part + second_part
    now = datetime.utcnow()
    new_code_to_add = NewEmailVerificationCode(
        code=code,
        email=email,
        creation=now,
        expiration=now + timedelta(minutes=mins),
    )
    try:
        await add_auth_code_to_db(new_code_to_add, session=session)
    except AddNewEmailVerificationCodeToDBError:
        raise CreateNewEmailVerificationCodeError
    return code
