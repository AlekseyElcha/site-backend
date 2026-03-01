from pydantic import BaseModel


class DatabaseConfig(BaseModel):
    user: str = "postgres"
    password: str = "postgres"
    host: str = "localhost"
    port: int = 6432
    db_name: str = "questions"

    max_pool_size: int = 10
    max_overflow: int = 10

    @property
    def async_url(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
