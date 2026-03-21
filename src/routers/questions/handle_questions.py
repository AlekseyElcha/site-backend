import uuid
from email.policy import HTTP
from typing import Annotated, Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from fastapi.params import Body, Form, File
from pyexpat.errors import messages
from sqlalchemy import True_
from sqlalchemy.ext.asyncio import AsyncSession

from exeptions import GetAllQuestionsListError, CreateNewAnswerError, GetUserEmailByQuestionErrorInEmailSender, \
    SendEmailError, UpdateQuestionStatusError, BasicOperationDatabaseError, GetUserEmailByQuestionError
from src.config.settings import settings
from src.database.crud.questions import (
    get_all_questions_from_db,
    change_question_status,
    get_answers_for_questions,
    get_answers_for_question_by_uuid,
    create_new_answer,
)
from src.database.db import get_session
from src.database.services.auxiliary import get_user_email_by_question_id
from src.models.models import Answers
from src.s3.operations import upload_multiple_files
from src.schemas.schemas import NewAnswerSchema
from src.services.email_service import send_notification_with_text

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
        session: Annotated[AsyncSession, Depends(get_session)]
):
    try:
        await change_question_status(question_id, new_status, session)
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
        answer: Annotated[str, Form()],
        session: Annotated[AsyncSession, Depends(get_session)],
        files: Optional[List[UploadFile]] = File(default=None),
):
    try:
        await create_new_answer_and_send_email(answer, session)
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
    except SendEmailError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при отправке email."
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
