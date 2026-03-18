import uuid

import pytz
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import time, timezone

from exeptions import CreateNewQuestionError, GetAllQuestionsListError, CreateNewAnswerError, \
    GetUserEmailByQuestionError, GetUserEmailByQuestionErrorInEmailSender, SendEmailError, UpdateQuestionStatusError, \
    BasicOperationDatabaseError, S3OperationsError
from src.database.services.auxiliary import get_user_email_by_question_id
from src.s3.operations import upload_multiple_files
from src.services.email_service import send_answer_email
from src.models.models import Questions, Answers
from src.schemas.schemas import NewQuestionSchema, NewAnswerSchema


async def create_new_question(
        question: NewQuestionSchema,
        session: AsyncSession,
):
    try:
        await upload_multiple_files(question, session)
    except:
        raise S3OperationsError

    new_question = Questions(
        id=question.id,
        name=question.name,
        surname=question.surname,
        email=question.email,
        address=question.address,
        message=question.message,
        files=question.files if question.files else [],
    )
    session.add(new_question)
    try:
        await session.commit()
    except:
        raise CreateNewQuestionError

    return new_question.id


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
        # for answer in result:
        #     utc_date = answer.__dict__.get("date")
        #     utc_time_str = str(answer.__dict__.get("time"))[:-7]
        #     utc_time = time.strptime(utc_time_str, "%H:%M:%S")
        #     converted_time = change_utc_date_and_time_into_local_tz(
        #         utc_time=utc_time,
        #         utc_date=utc_date,
        #         local_tz=local_timezone,
        #     )
        #     answer["date"] = converted_time.split()[0]
        #     answer["time"] = converted_time.split()[1]
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


async def get_question_by_uuid(question_uuid: str, session: AsyncSession):
    query = select(Questions).where(Questions.id == question_uuid)
    try:
        data = await session.execute(query)
        result = data.scalars().first()
        return result
    except:
        raise BasicOperationDatabaseError
