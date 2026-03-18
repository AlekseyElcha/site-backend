import datetime
import uuid
from typing import Annotated, List, Optional, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException, Form, UploadFile, File
from fastapi.params import Path
from sqlalchemy.ext.asyncio import AsyncSession

from exeptions import CreateNewQuestionError, S3OperationsError
from src.auth.code_generator import generate_auth_code_and_and_to_db
from src.auth.utils import validate_auth_user
from src.database.crud.questions import create_new_question, get_question_by_uuid
from src.database.db import get_session
from src.models.models import Questions
from src.s3.operations import upload_multiple_files
from src.schemas.schemas import UserSchema, NewQuestionSchema, UserAuthSchema
from src.auth.autherization import auth_user_check_self_info

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
    filenames = []
    if files:
        for file in files:
            old_filename = file.filename
            new_filename = (f"{old_filename}_{datetime.datetime.now(datetime.timezone.utc)}UTC_"
                            f"{str(uuid.uuid4())[:4]}.{old_filename.split('.')[-1]}")
            filenames.append(new_filename)
            file.filename = new_filename
        question_data.files = filenames
    try:
        question_id = await create_new_question(question_data, session)
    except CreateNewQuestionError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла ошибка при создании вопроса.",
        )
    if files:
        try:
            await upload_multiple_files(
                files=files,
                question_uuid=question_id,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при загрузке!"
            )
    return {
        "message": "Вопрос успешно создан."
    }
