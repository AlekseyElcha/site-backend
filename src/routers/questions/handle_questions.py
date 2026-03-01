from email.policy import HTTP
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Body
from pyexpat.errors import messages
from sqlalchemy import True_
from sqlalchemy.ext.asyncio import AsyncSession

from exeptions import GetAllQuestionsListError, CreateNewAnswerError, GetUserEmailByQuestionErrorInEmailSender, \
    SendEmailError, UpdateQuestionStatusError
from src.database.crud.questions import get_all_questions_from_db, create_new_answer_and_send_email, \
    change_question_status
from src.database.db import get_session
from src.models.models import Answers
from src.schemas.schemas import NewAnswerSchema

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
async def test(
        answer: NewAnswerSchema,
        session: Annotated[AsyncSession, Depends(get_session)]
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
        await change_question_status(
            question_id=answer.question_id,
            new_status="answered",
            session=session
        )
    except UpdateQuestionStatusError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось обновить статус вопроса."
        )
    return {
        "message": f"Ответ на вопрос {answer.question_id} успешно создан и отправлен. "
                   f"Статус вопроса был автоматически обновлён до «Отвечено»."
    }
