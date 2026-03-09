from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from exeptions import BasicOperationDatabaseError
from src.models.models import AllUsers
from src.schemas.schemas import UserAddSchema


async def get_user_role_if_user_exists_else_create_new_user(user_email: str, session: AsyncSession):
    query = (select(AllUsers).where(AllUsers.email == user_email))
    try:
        res = await session.execute(query)
        data = res.scalars().first()
        if not data:
            await create_new_user(user=UserAddSchema(email=user_email, role="user"), session=session)
        else:
            return data.role
    except:
        raise BasicOperationDatabaseError


async def create_new_user(user: UserAddSchema, session: AsyncSession):
    new_user = AllUsers(email=user.email,
                             role=user.role,
    )
    session.add(new_user)
    try:
        await session.commit()
        await session.refresh(new_user)
        return user.role
    except:
        raise BasicOperationDatabaseError