from redis.asyncio import Redis
from functools import lru_cache

from src.config.settings import settings


@lru_cache
def get_redis():
    return Redis(
        host=settings.redis.host,
        port=settings.redis.port
    )
