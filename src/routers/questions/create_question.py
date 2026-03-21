import datetime
import uuid
from email import message_from_file
from typing import Annotated, List, Optional, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException, Form, UploadFile, File
from fastapi.params import Path
from sqlalchemy.ext.asyncio import AsyncSession

from exeptions import CreateNewQuestionError, S3OperationsError
from src.auth.code_generator import generate_auth_code_and_and_to_db
from src.auth.utils import validate_auth_user
from src.config.settings import settings
from src.database.crud.questions import create_new_question, get_question_by_uuid
from src.database.db import get_session
from src.models.models import Questions
from src.s3.operations import upload_multiple_files
from src.schemas.schemas import UserSchema, NewQuestionSchema, UserAuthSchema
from src.auth.autherization import auth_user_check_self_info
from src.services.email_service import send_notification_with_text

router = APIRouter(
    prefix="/questions",
    tags=["questions"],
)

@router.post("/create_question")
async def create_question(
        session: Annotated[AsyncSession, Depends(get_session)],
        current_user: Annotated[Dict[str, str], Depends(auth_user_check_self_info)],
        question: Annotated[str, Form()],
        files: Optional[List[UploadFile]] = File(default=None),
):
    question_data = NewQuestionSchema.model_validate_json(question)
    unique_id = uuid.uuid4()
    filenames = []
    if files:
        for file in files:
            old_filename = file.filename
            new_filename = (f"{old_filename}_"
                            f"{unique_id}.{old_filename.split('.')[-1]}")
            filenames.append(new_filename)
            file.filename = new_filename
        question_data.files = filenames
    try:
        await create_new_question(question_data, unique_id, session)
    except CreateNewQuestionError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла ошибка при создании вопроса.",
        )
    if files:
        try:
            await upload_multiple_files(
                files=files,
                question_uuid=unique_id,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при загрузке!"
            )
    try:
        # TODO поменять ссылки здесь!!!
        await send_notification_with_text(
            email=question_data.email,
            subject="ООО «Домофон-сервис». Уведомление о создании обращения",
            message=f"Уважаемый {question_data.name} {question_data.surname},\n"
                    f"Уведомляем Вас о том, что Вы успешно создали обращение в ООО «Домофон-сервис» "
                    f"при помощи нашего онлайн-сервиса <ССЫЛКУ СЮДА> \n\n"
                    f"Если Вы не оставляли обращение, напишите <СЮДА> - со всем разберёмся.\n"
                    f"Уникальный идентификатор вопроса: {unique_id}\n\n"
                    f"Данное письмо было отправлено автоматически, просьба не отвечать на него."
        )
    except:
        print("Ошибка при отправке нотификации user, но вопрос создан")
    try:
        await send_notification_with_text(
            email=settings.email.from_address,
            subject="Уведомление о новом обращении на платформе",
            message=f"Было создано новое обращение на платформе.\n"
                    f"Ссылка на обращение: http://localhost:3000/admin/{unique_id}\n\n"
                    f"Базовая информация об обращении:\n"
                    f"{question_data}"
        )
    except:
        print("Ошибка при отправке нотификации admin, но вопрос создан")
    return {
        "message": "Вопрос успешно создан."
    }
