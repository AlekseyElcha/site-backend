from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter

from src.database.db import engine
from src.models.models import Base
from src.routers.questions.create_question import router as questions_router
from src.routers.questions.handle_questions import router as handle_questions_router
from src.auth.autherization import router as auth_router
from src.s3.operations import router as files_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {
        "message": "working",
    }

app.include_router(router=questions_router)
app.include_router(router=handle_questions_router)
app.include_router(router=auth_router)
app.include_router(router=files_router)


# TODO добавить удаление email-кода из БД после изменения статуса на was_used=True - опционально (нагрузка низкая)
# TODO разобраться с фильтрацией (поиском) обращений по id, name, surname, email и address - !!!
