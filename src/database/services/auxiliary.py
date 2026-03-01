import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from exeptions import GetUserEmailByQuestionError
from src.models.models import Questions


async def get_user_email_by_question_id(
        session: AsyncSession,
        question_id: uuid.UUID
):
    query = select(Questions.email).where(Questions.id == question_id)
    try:
        data = await session.execute(query)
        user_email = data.scalars().first()
    except:
        raise GetUserEmailByQuestionError
    return user_email
