from contextlib import asynccontextmanager

import redis
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from src.database.db import engine
from src.models.models import Base
from src.redis.get_redis import get_redis
from src.routers.questions.create_question import router as questions_router
from src.routers.questions.handle_questions import router as handle_questions_router
from src.auth.autherization import router as auth_router
from src.s3.operations import router as files_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    redis_client = get_redis()
    yield
    await redis_client.aclose()


app = FastAPI(lifespan=lifespan)


origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "working",
    }

app.include_router(router=questions_router)
app.include_router(router=handle_questions_router)
app.include_router(router=auth_router)
app.include_router(router=files_router)


# TODO добавить обработку ошибки на handle_questions/change_question_status
# TODO проверить отправку файлов (кодировку) с разных ОС

