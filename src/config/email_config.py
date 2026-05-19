import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class EmailServiceConfig(BaseModel):
    # неактуально, т.к. smtp-порты заблокированы на VPS
    from_address: str = os.getenv("MAIL_FROM_ADDRESS")
    password: str = os.getenv("MAIL_SERVICE_SECRET")
    smtp: str = "smtp.mail.ru"
    port: int = 587

    # обход блокировки портов на VPS через "Resend"
    resend_api_key = os.getenv("RESEND_API_KEY")

    from_email: str = "ООО \"Домофон-сервис\" <noreply@domofon-servis-odi.ru>"


    # TODO Поменять!!!!!!!
    url_to_personal_account: str = "http://test.domofon-servis-odi.ru/user/"
    url_to_admin_account: str = "http://test.domofon-servis-odi.ru/admin/"

    # retries_for_sending_messages: int = 3

    send_answer_email_mod_retries: int = 2
    send_answer_email_mod_delay: int = 2
    send_answer_email_mod_backoff: int = 2

    send_auth_code_retries: int = 2
    send_auth_code_delay: int = 1.0
    send_auth_code_backoff: int = 2.0

    send_notification_with_text_retries: int = 2
    send_notification_with_text_delay: float = 1.0
    send_notification_with_text_backoff: float = 2.0
