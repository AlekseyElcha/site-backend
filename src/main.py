from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter

from src.database.db import engine
from src.models.models import Base
from src.routers.questions.create_question import router as questions_router
from src.routers.questions.handle_questions import router as handle_questions_router

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
