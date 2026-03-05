import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

from exeptions import SendEmailError

# TODO вынести параметры в конфиг, обновить код


load_dotenv()
async def send_answer_email(user_email: str, message: str):
    fromaddr = "alekseyelcha07@mail.ru"
    toaddr = f"{user_email}"
    passw = os.getenv("MAIL_SERVICE_SECRET")

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Ответ // тест"

    body = (f"{message}")
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP_SSL('smtp.mail.ru', 465)

        server.login(fromaddr, passw)

        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        print("Письмо успешно отправлено!")

    except Exception as e:
        raise SendEmailError


# async def send_reset_password_email_notification(user_email: str):
#     fromaddr = "alekseyelcha07@mail.ru"
#     toaddr = f"{user_email}"
#     passw = os.getenv("MAIL_SERVICE_SECRET")
#
#     msg = MIMEMultipart()
#     msg['From'] = fromaddr
#     msg['To'] = toaddr
#     msg['Subject'] = "LinkShortener // Ваш пароль был обновлён"
#
#     body = (f"Внимание! Ваш пароль от аккаунта {user_email} был успешно обновлён!\n"
#             f"\n"
#         f"Если это были не Вы, немедленно восстановите доступ: "
#     f"Перейдите на http://localhost:8000/, нажмите на кнопку «Войти» в правом верхнем углу и нажмите на «Не помню пароль»\n"
#     f"Далее, следуя инструкции, обновите пароль!\n"
#     f"\n"
#     f"В случае возникновения проблем обратитесь в поддержку, написав на этот email.")
#     msg.attach(MIMEText(body, 'plain', 'utf-8'))
#
#     try:
#         server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
#
#         server.login(fromaddr, passw)
#
#         text = msg.as_string()
#         server.sendmail(fromaddr, toaddr, text)
#         print("Письмо успешно отправлено!")
#
#     except Exception as e:
#         raise SendEmailError



# async def send_email_validation(user_email: str, validate_url: str):
#     fromaddr = "alekseyelcha07@mail.ru"
#     toaddr = f"{user_email}"
#     passw = os.getenv("MAIL_SERVICE_SECRET")
#
#     msg = MIMEMultipart()
#     msg['From'] = fromaddr
#     msg['To'] = toaddr
#     msg['Subject'] = "LinkShortener // Подтвердите email для создания аккаунта"
#
#     body = (f"Перейдите по ссылке: {validate_url} для завершения регистрации!")
#     msg.attach(MIMEText(body, 'plain', 'utf-8'))
#
#     try:
#         server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
#
#         server.login(fromaddr, passw)
#
#         text = msg.as_string()
#         server.sendmail(fromaddr, toaddr, text)
#         print("Письмо успешно отправлено!")
#
#     except Exception as e:
#         raise SendEmailError
