import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from src.config.settings import settings
from exeptions import SendEmailError


load_dotenv()
async def send_answer_email(user_email: str, message: str):
    fromaddr = settings.email.from_address
    toaddr = f"{user_email}"
    passw = settings.email.password

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Ответ // тест"

    body = (f"{message}")
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP_SSL(settings.email.smtp, settings.email.port)

        server.login(fromaddr, passw)

        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        print("Письмо успешно отправлено!")

    except Exception as e:
        raise SendEmailError

async def send_auth_code(user_email: str, auth_code: str):
    fromaddr = settings.email.from_address
    toaddr = f"{user_email}"
    passw = settings.email.password

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Код для входа // тест"

    body = (f"Ваш код для входа на сайт: {auth_code}\n"
            f"Код действителен в течение {settings.business.email_code_verification_timeout_minutes} минут.\n\n"
            f"Данное письмо было отправлено автоматически.")
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP_SSL(settings.email.smtp, settings.email.port)

        server.login(fromaddr, passw)

        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        print("Письмо успешно отправлено!")

    except Exception as e:
        raise SendEmailError


async def send_notification_with_text(email: str, subject: str , message: str):
    fromaddr = settings.email.from_address
    toaddr = email
    passw = settings.email.password

    msg = MIMEMultipart()
    msg["From"] = fromaddr
    msg["To"] = toaddr
    msg["Subject"] = subject
    body = message
    msg.attach(MIMEText(body, "plain", "utf-8"))
    try:
        server = smtplib.SMTP_SSL(settings.email.smtp, settings.email.port)

        server.login(fromaddr, passw)

        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        print("Письмо успешно отправлено!")

    except Exception as e:
        raise SendEmailError
