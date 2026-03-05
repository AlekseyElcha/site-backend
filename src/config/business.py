from pydantic import BaseModel

class Business(BaseModel):
    email_code_verification_timeout_minutes: int = 60


