from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from exeptions import CreateNewQuestionError
from src.database.crud.questions import create_new_question
from src.database.db import get_session
from src.models.models import Questions
from src.schemas.schemas import UserSchema, NewQuestionSchema

router = APIRouter(
    prefix="/questions",
    tags=["questions"],
)

@router.post("/create_question")
async def create_question(
        question: NewQuestionSchema,
        session: Annotated[AsyncSession, Depends(get_session)]
):
    try:
        await create_new_question(question, session)
    except CreateNewQuestionError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла ошибка при создании вопроса.",
        )
    return {
        "message": "Вопрос успешно создан."
    }
