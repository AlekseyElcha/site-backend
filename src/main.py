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


# t0d0 передалать нейминг файлов при загрузке (время + название от абонента + уникальная последовательность) - сделано
# TODO сделать оповещение на основную почту о создании пользователем нового обращения
# TODO добавить оповещение пользователю о получении ответа
# TODO сделать отображение загруженных файлов у абонента и админа
# TODO добавить возможность менять состояние вопроса в архивное
# TODO добавить удаление email-кода из БД после изменения статуса на was_used=True

