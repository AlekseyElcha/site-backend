from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    name: str
    surname: str
    address: str
    email: EmailStr


class NewQuestionSchema(BaseModel):
    name: str
    email: EmailStr
    surname: str
    address: str
    message: str


class NewAnswerSchema(BaseModel):
    message: str
    question_id: str
