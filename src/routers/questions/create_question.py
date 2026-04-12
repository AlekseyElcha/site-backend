import uuid
import logging
from typing import Annotated, List, Optional, Dict
from fastapi import APIRouter, Depends, status, HTTPException, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
from exceptions import CreateNewQuestionError
from src.database.crud.questions import create_new_question
from src.database.db import get_session
from src.models.models import Questions
from src.s3.operations import upload_multiple_files
from src.schemas.schemas import UserSchema, NewQuestionSchema, UserAuthSchema
from src.auth.autherization import auth_user_check_self_info
from src.config.settings import settings
from src.services.email_service import send_notification_with_text
from exceptions import SendEmailError


logging.basicConfig(
    level=settings.logs.level,
    datefmt=settings.logs.datefmt,
    format=settings.logs.format,
)
logger = logging.getLogger(__name__)


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
        logger.warning("ОШИБКА ПРИ СОЗДАНИИ ВОПРОСА!")
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
            logger.warning("ОШИБКА ПРИ ЗАГРУЗКЕ ФАЙЛОВ {}".format(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при загрузке!"
            )
    try:
        # TODO поменять ссылки здесь!!!
        await send_notification_with_text(
            email=question_data.email.lower(),
            subject="ООО «Домофон-сервис». Уведомление о создании обращения",
            message=settings.business.format_message_text(
                question_data.name, question_data.surname, unique_id
            ),
        )
    except SendEmailError:
        # success = False
        retries_count = settings.email.retries_for_sending_messages
        for retry in range(retries_count):
            logger.warning(
                "Ошибка при отправке email на: {}."
                " об успешном создании обращения."
                .format(question_data.email)
            )
        #     await asyncio.sleep(5)
        #     try:
        #         await send_notification_with_text(
        #             email=question_data.email.lower(),
        #             subject="ООО «Домофон-сервис». Уведомление о создании обращения",
        #             message=settings.business.format_message_text(
        #                 question_data.name,
        #                 question_data.surname,
        #                 unique_id
        #             ),
        #         )
        #         success = True
        #     except SendEmailError:
        #         logger.warning(
        #             "RETRY {} UNSUCCESSFUL. RETRYING AFTER 5 SECONDS".format(retry+1)
        #         )
        # if not success:
        #     logger.warning("{} RETRIES UNSUCCESSFUL.".format(retries_count))
    try:
        await send_notification_with_text(
            email=settings.email.from_address.lower(),
            subject="Уведомление о новом обращении на платформе",
            message=settings.business.format_message_text_for_admins(
                unique_id, question_data
            )
        )
    except:
        # success = False
        logger.warning("Ошибка при отправке сообщения о новом обращении админам.")
        # await asyncio.sleep(5)
        # retries_count = settings.email.retries_for_sending_messages
        # for retry in range(retries_count):
        #     try:
        #         await send_notification_with_text(
        #             email=settings.email.from_address.lower(),
        #             subject="Уведомление о новом обращении на платформе",
        #             message=settings.business.format_message_text_for_admins(
        #                 unique_id, question_data
        #             )
        #         )
        #         success = True
        #     except SendEmailError:
        #         logger.warning(
        #             "RETRY {} UNSUCCESSFUL. RETRYING AFTER 5 SECONDS".format(retry+1)
        #         )
        #     if not success:
        #         logger.warning("{} RETRIES UNSUCCESSFUL.".format(retries_count))

    return {
        "message": "Вопрос успешно создан."
    }
