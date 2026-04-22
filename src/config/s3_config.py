from dotenv import load_dotenv
from pydantic import BaseModel
import os

load_dotenv()

class S3Settings(BaseModel):
    key: str = os.getenv("KEY_ID")
    secret: str = os.getenv("SECRET")
    endpoint: str = os.getenv("ENDPOINT")
    container: str = os.getenv("CONTAINER")
    url_expiration: int = 86400 # 24 часа
