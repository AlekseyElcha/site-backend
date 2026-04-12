import uuid
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from exceptions import GetUserEmailByQuestionError, BasicOperationDatabaseError
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


async def get_question_data_by_question_id(
        question_id: UUID,
        session: AsyncSession
):
    query = select(Questions).where(Questions.id == question_id)
    try:
        data = await session.execute(query)
        question_data = data.scalars().first()
    except:
        raise BasicOperationDatabaseError
    return question_data
