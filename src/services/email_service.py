import smtplib
import asyncio
import aiohttp
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from sqlalchemy import except_all

from src.config.settings import settings
from exceptions import SendEmailError
from src.decorators.retrying import retry
from src.routers.questions.create_question import logger
from src.services.email_service_v2 import send_email

load_dotenv()

SEND_ANSWER_EMAIL_MOD_MAX_ATTEMPTS = settings.email.send_answer_email_mod_retries
SEND_ANSWER_EMAIL_DELAY = settings.email.send_answer_email_mod_delay
SEND_ANSWER_EMAIL_BACKOFF = settings.email.send_answer_email_mod_backoff

SEND_AUTH_CODE_MAX_ATTEMPTS = settings.email.send_auth_code_retries
SEND_AUTH_CODE_DELAY = settings.email.send_auth_code_delay
SEND_AUTH_CODE_BACKOFF = settings.email.send_auth_code_backoff

SEND_NOTIFICATION_WITH_TEXT_MAX_ATTEMPTS = settings.email.send_notification_with_text_retries
SEND_NOTIFICATION_WITH_TEXT_DELAY = settings.email.send_notification_with_text_delay
SEND_NOTIFICATION_WITH_TEXT_BACKOFF = settings.email.send_notification_with_text_backoff


# не работает на VPS!!!
@retry(
    max_attempts=SEND_ANSWER_EMAIL_MOD_MAX_ATTEMPTS,
    delay=SEND_ANSWER_EMAIL_DELAY,
    backoff=SEND_ANSWER_EMAIL_BACKOFF,
)
async def send_answer_email_mod(user_email: str, message: str):
    fromaddr = settings.email.from_address
    toaddr = f"{user_email.lower()}"
    passw = settings.email.password

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = settings.business.send_answer_email_mod_subject
    body = (f"{message}")
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # await asyncio.to_thread(_send_email_sync, fromaddr, toaddr, passw, msg)


# async def send_answer_email_autocreated_by_question_id(question_id: UUID):
#
#     fromaddr = settings.email.from_address
#     toaddr = f"{user_email.lower()}"
#     passw = settings.email.password
#
#     msg = MIMEMultipart()
#     msg['From'] = fromaddr
#     msg['To'] = toaddr
#     msg['Subject'] = f"ООО «Домофон-сервис». Ответ на Ваш вопрос."
#     body = (f"{message}")
#     msg.attach(MIMEText(body, 'plain', 'utf-8'))
#
#     try:
#         server = smtplib.SMTP_SSL(settings.email.smtp, settings.email.port)
#
#         server.login(fromaddr, passw)
#
#         text = msg.as_string()
#         server.sendmail(fromaddr, toaddr, text)
#         print("Письмо успешно отправлено!")
#
#     except Exception as e:
#         raise SendEmailError


@retry(
    max_attempts=SEND_NOTIFICATION_WITH_TEXT_MAX_ATTEMPTS,
    delay=SEND_NOTIFICATION_WITH_TEXT_DELAY,
    backoff=SEND_NOTIFICATION_WITH_TEXT_BACKOFF,
)
async def send_auth_code(user_email: str, auth_code: str):
    # fromaddr = settings.email.from_address
    toaddr = f"{user_email}"
    # passw = settings.email.password

    # msg = MIMEMultipart()
    # msg['From'] = fromaddr
    # msg['To'] = toaddr
    # msg['Subject'] = settings.business.send_auth_code_subject
    subject = settings.business.send_auth_code_subject
    body = settings.business.format_auth_code_message(
        auth_code,
        settings.business.email_code_verification_timeout_minutes
    )
    # msg.attach(MIMEText(body, 'plain', 'utf-8'))
    try:
        await send_email(
            user_email=toaddr,
            subject=subject,
            message=body,
        )
    except Exception as e:
        logger.warning(e)
        raise SendEmailError

# не работает
# @retry(
#     max_attempts=SEND_NOTIFICATION_WITH_TEXT_MAX_ATTEMPTS,
#     delay=SEND_NOTIFICATION_WITH_TEXT_DELAY,
#     backoff=SEND_NOTIFICATION_WITH_TEXT_BACKOFF,
# )
# async def send_notification_with_text(email: str, subject: str , message: str):
#     fromaddr = settings.email.from_address
#     toaddr = email
#     passw = settings.email.password
#
#     msg = MIMEMultipart()
#     msg["From"] = fromaddr
#     msg["To"] = toaddr
#     msg["Subject"] = subject
#     body = message
#     msg.attach(MIMEText(body, "plain", "utf-8"))
#
#     await ...
