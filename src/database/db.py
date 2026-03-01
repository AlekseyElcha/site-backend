from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.config.settings import settings

database_url = settings.db.async_url

print(database_url)

engine = create_async_engine(
    url=database_url,
    pool_size=5,
    max_overflow=5,
    pool_pre_ping=True
)

async_session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

async def get_session():
    async with async_session_maker() as session:
        yield session