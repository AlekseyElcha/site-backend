import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class EmailServiceConfig(BaseModel):
    from_address: str = "alekseyelcha07@mail.ru"
    password: str = os.getenv("MAIL_SERVICE_SECRET")
    smtp: str = "smtp.mail.ru"
    port: int = 465
