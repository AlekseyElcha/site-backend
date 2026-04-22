from pydantic import BaseModel
import os

class RedisConfig(BaseModel):
    host: str = os.getenv("REDIS_HOST", "localhost")
    port: int = int(os.getenv("REDIS_PORT", "6379"))
    expiration_seconds: int = 60


