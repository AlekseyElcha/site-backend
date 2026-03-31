import asyncio
import logging
import uuid
from email.policy import HTTP
from typing import Annotated, Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Request
from fastapi.params import Body, Form, File
from pyexpat.errors import messages
from sqlalchemy import True_
from sqlalchemy.ext.asyncio import AsyncSession
from exceptions import GetAllQuestionsListError, CreateNewAnswerError, GetUserEmailByQuestionErrorInEmailSender, \
    SendEmailError, UpdateQuestionStatusError, BasicOperationDatabaseError, GetUserEmailByQuestionError, \
    CreateNewExtraMessageError
from src.config.settings import settings
from src.database.crud.questions import (
    get_all_questions_from_db,
    change_question_status,
    get_answers_for_questions,
    get_answers_for_question_by_uuid,
    create_new_answer, create_extra_message_for_question,
)
from src.database.db import get_session
from src.database.services.auxiliary import get_user_email_by_question_id
from src.models.models import Answers
from src.s3.operations import upload_multiple_files
from src.schemas.schemas import NewAnswerSchema, NewExtraMessageSchema
from src.services.email_service import send_notification_with_text
from src.services.token_service import check_admin, get_current_user

logging.basicConfig(
    level=settings.logs.level,
    datefmt=settings.logs.datefmt,
    format=settings.logs.format,
)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/handle_questions",
    tags=["questions"],
)

@router.get("/all_questions")
async def get_all_questions(session: Annotated[AsyncSession, Depends(get_session)]):
    try:
        data = await get_all_questions_from_db(session)
    except GetAllQuestionsListError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении списка вопросов.")
    return data


@router.get("/answers_for_all_questions")
async def get_all_answers_for_all_questions(
        session: Annotated[AsyncSession, Depends(get_session)]
):
    try:
        data = await get_answers_for_questions(session=session)
    except BasicOperationDatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при работе с базой данных"
        )
    return data


@router.get("/answers_for_question/{question_id}")
async def get_all_answers_for_all_questions(
        question_id: UUID,
        session: Annotated[AsyncSession, Depends(get_session)]
):
    try:
        data = await get_answers_for_question_by_uuid(question_uuid=question_id, session=session)
    except BasicOperationDatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при работе с базой данных"
        )
    return data

@router.put("/change_question_status")
async def change_question_status_manually(
        question_id: Annotated[str, Body(embed=True)],
        new_status: Annotated[str, Body(embed=True)],
        user_data: Annotated[dict, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_session)]
):
    user_role = user_data.get("role")
    try:
        await change_question_status(question_id, new_status, user_role, session)
    except UpdateQuestionStatusError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении статуса вопроса {question_id}."
        )
    return {
        "message": "Статус вопроса успешно обновлён."
    }

@router.post("/answer_question")
async def answer_question(
        # answer: NewAnswerSchema
        request: Request,
        answer: Annotated[str, Form()],
        session: Annotated[AsyncSession, Depends(get_session)],
        admin: Annotated[bool, Depends(check_admin)],
        files: Optional[List[UploadFile]] = File(default=None),
):
    answer_data = NewAnswerSchema.model_validate_json(answer)
    if files:
        filenames = []
        for file in files:
            old_filename = file.filename
            new_filename = (
                f"{old_filename}_" f"{answer_data.question_id}_answer.{old_filename.split('.')[-1]}"
            )
            filenames.append(new_filename)
            file.filename = new_filename
        answer_data.files = filenames
    try:
        user_email = await get_user_email_by_question_id(
            question_id=answer_data.question_id,
            session=session
        )
    except GetUserEmailByQuestionError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении email при помощи id вопроса."
        )
    try:
        await create_new_answer(answer_data, session)
    except CreateNewAnswerError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании ответа."
        )
    except GetUserEmailByQuestionErrorInEmailSender:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении почты по идентификатору вопроса."
        )
    if files:
        try:
            await upload_multiple_files(
                files=files,
                question_uuid=answer_data.question_id,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при загрузке!"
            )
    try:
        await send_notification_with_text(
            email=user_email,
            subject="ООО «Домофон-сервис». На Ваш вопрос поступил ответ.",
            message=f"На Ваш вопрос {answer_data.question_id} поступил ответ.\n"
                    f"Ознакомиться с ним Вы можете на нашей платформе по ссылке"
                    f" {settings.email.url_to_personal_account}{answer_data.question_id}.\n\n"
                    f"Данное сообщение было отправлено автоматически, просьба не отвечать на него."
        )
    except:
        print("Ошибка при отправке нотификации user с ответом.")
    try:
        await change_question_status(
            question_id=answer_data.question_id,
            user_role="admin",
            new_status="answered",
            session=session
        )
    except UpdateQuestionStatusError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось обновить статус вопроса."
        )
    return {
        "message": f"Ответ на вопрос {answer_data.question_id} успешно создан и отправлен. "
                   f"Статус вопроса был автоматически обновлён до «Отвечено»."
    }



@router.post("/create_extra_message")
async def add_extra_message_to_question(
        request: Request,
        question_id: Annotated[UUID, Body(embed=True)],
        message: Annotated[str, Body(embed=True)],
        files: Optional[List[UploadFile]] = File(default=None),
        session: AsyncSession = Depends(get_session),
):
    message_data = NewExtraMessageSchema.model_validate_json(message)
    unique_id = uuid.uuid4()
    filenames = []
    if files:
        for file in files:
            old_filename = file.filename
            new_filename = (f"{old_filename}_"
                            f"{unique_id}.{old_filename.split('.')[-1]}")
            filenames.append(new_filename)
            file.filename = new_filename
        message_data.files = filenames
    # try:
    await create_extra_message_for_question(message_data, unique_id, session)
    # except CreateNewExtraMessageError:
    #     logger.warning("ERROR WHILE CREATING NEW QUESTION")
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail="Произошла ошибка при создании вопроса.",
    #     )
    if files:
        try:
            await upload_multiple_files(
                files=files,
                question_uuid=unique_id,
            )
        except Exception as e:
            logger.warning("ERROR WHILE UPLOADING FILES {}".format(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при загрузке!"
            )
    try:
        await send_notification_with_text(
            email=settings.email.from_address.lower(),
            subject="Уведомление о новом сообщении",
            message=settings.business.format_message_text_for_admins(
                unique_id, message_data
            )
        )
    except:
        success = False
        logger.warning("ERROR WHILE SENDING QUESTION CREATED TO ADMIN. RETRYING AFTER 5 SEC.")
        await asyncio.sleep(5)
        retries_count = settings.email.retries_for_sending_messages
        for retry in range(retries_count):
            try:
                await send_notification_with_text(
                    email=settings.email.from_address.lower(),
                    subject="Уведомление о новом сообщении",
                    message=settings.business.format_extra_message_text(
                        unique_id, message_data
                    )
                )
                success = True
            except SendEmailError:
                logger.warning(
                    "RETRY {} UNSUCCESSFUL. RETRYING AFTER 5 SECONDS".format(retry + 1)
                )
            if not success:
                logger.warning("{} RETRIES UNSUCCESSFUL.".format(retries_count))

    return {
        "message": "Вопрос успешно создан."
    }
