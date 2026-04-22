from pydantic import BaseModel
import os


class DatabaseConfig(BaseModel):
    user: str = os.getenv("DB_USER", "postgres")
    password: str = os.getenv("DB_PASSWORD", "postgres")
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "6432"))
    db_name: str = os.getenv("DB_NAME", "questions")

    max_pool_size: int = 10
    max_overflow: int = 10

    @property
    def async_url(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"

    @property
    def sync_url(self):
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
