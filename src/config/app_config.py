from pathlib import Path

from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class AppConfig(BaseModel):
    title: str = "Mail Questions Test"
    host: str = "0.0.0.0"
    port: int = 8000
