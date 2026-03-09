import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from exeptions import CreateNewQuestionError, GetAllQuestionsListError, CreateNewAnswerError, \
    GetUserEmailByQuestionError, GetUserEmailByQuestionErrorInEmailSender, SendEmailError, UpdateQuestionStatusError, \
    BasicOperationDatabaseError
from src.database.services.auxiliary import get_user_email_by_question_id
from src.services.email_service import send_answer_email
from src.models.models import Questions, Answers
from src.schemas.schemas import NewQuestionSchema, NewAnswerSchema


async def create_new_question(
        question: NewQuestionSchema,
        session: AsyncSession,
):
    new_question = Questions(
        name=question.name,
        surname=question.surname,
        email=question.email,
        address=question.address,
        message=question.message,
    )
    session.add(new_question)
    try:
        await session.commit()
    except:
        raise CreateNewQuestionError

    return True


async def get_all_questions_from_db(session: AsyncSession):
    query = select(Questions)
    try:
        result = await session.execute(query)
    except:
        raise GetAllQuestionsListError
    await session.close()
    return result.scalars().all()


async def create_new_answer_and_send_email(
        answer: NewAnswerSchema,
        session: AsyncSession,
):
    new_answer = Answers(
        message=answer.message,
        question_id=answer.question_id,
    )
    session.add(new_answer)
    try:
        await session.commit()
    except:
        raise CreateNewAnswerError
    await session.close()
    try:
        await send_answer_email(
            user_email=await get_user_email_by_question_id(session, answer.question_id),
            message=answer.message,
        )
    except GetUserEmailByQuestionError:
        raise GetUserEmailByQuestionErrorInEmailSender
    except SendEmailError:
        raise SendEmailError
    return True


async def change_question_status(
        question_id: uuid.UUID,
        new_status: str,
        session: AsyncSession,
):
    query = update(Questions).where(Questions.id == question_id).values(status=new_status)
    try:
        await session.execute(query)
    except:
        raise UpdateQuestionStatusError
    await session.commit()
    return True


async def get_answers_for_questions(session: AsyncSession):
    query = select(Answers)
    try:
        data = await session.execute(query)
        result = data.scalars().all()
        return result
    except:
        raise BasicOperationDatabaseError


async def get_answers_for_question_by_uuid(question_uuid: str, session: AsyncSession):
    query = select(Answers).where(Answers.question_id == question_uuid)
    try:
        data = await session.execute(query)
        result = data.scalars().all()
        return result
    except:
        raise BasicOperationDatabaseError
