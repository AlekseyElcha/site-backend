from pydantic import BaseModel

class AppConfig(BaseModel):
    title: str = "Mail Questions Test"
    host: str = "0.0.0.0"
    port: int = 8000
