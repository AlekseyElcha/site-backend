import asyncio
import json

from exceptions import RedisOpsBasicException
from src.config.settings import settings
from src.redis.get_redis import get_redis

redis_client = get_redis()

auth_code_timeout_sec = settings.auth_jwt.access_expiration_timeout_minutes * 60

async def add_auth_code_to_redis(
        email: str,
        auth_code: str,
):
    key = f"auth:{auth_code}:{email}"
    data = {
        "email": email,
        "auth_code": auth_code,
    }

    json_data = json.dumps(data)

    try:
        await redis_client.setex(
            key,
            settings.auth_jwt.access_expiration_timeout_minutes,
            json_data
        )
    except:
        raise RedisOpsBasicException


async def find_code_in_redis(
        email: str,
        auth_code: str
):
    key = f"auth:{auth_code}:{email}"
    try:
        data = await redis_client.get(key)
        if data:
            return True
        return False
    except:
        raise RedisOpsBasicException






# Тестирование
# async def main():
#     # Запускаем всё в одном цикле событий (event loop),
#     # чтобы не плодить asyncio.run на каждый чих
#     await add_auth_code_to_redis(
#         email="test_email@test.test",
#         auth_code="123457"
#     )
#     print("1: Код успешно записан")
#
#     status = await find_code_in_redis(
#         email="test_email@test.test",
#         auth_code="12351"
#     )
#     print(f"2: Статус поиска: {status}")
#
# if __name__ == "__main__":
#     asyncio.run(main())