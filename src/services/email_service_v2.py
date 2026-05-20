import asyncio
import aiohttp

from exceptions import SendEmailError
from src.config.settings import settings


async def send_email(user_email: str | list[str], subject: str, message: str):
    if isinstance(user_email, str):
        recipients = [user_email]
    else:
        recipients = user_email

    async with aiohttp.ClientSession() as session:
        async with session.post(
                "https://api.resend.com/emails",
                json={
                    "from": settings.email.from_email,
                    "to": recipients,
                    "subject": subject,
                    "text": message,
                },
                headers={
                    "Authorization": f"Bearer {settings.email.resend_api_key}",
                    "Content-Type": "application/json",
                },
        ) as response:
            data = await response.json()

            if response.status == 200:
                print(f"Письмо отправлено, id: {data.get('id')}")
            else:
                raise SendEmailError(
                    f"Resend API error {response.status}: {data.get('message')}"
                )
# testing
# asyncio.run(
#     send_email(
#         user_email="aleshus2007@gmail.com",
#         subject="TEST",
#         message="test message",
#     )
# )