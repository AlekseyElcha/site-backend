from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, EmailStr
from datetime import date, time, datetime


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
    files: Optional[List[str]] = None


class NewAnswerSchema(BaseModel):
    message: str
    question_id: str
    files: Optional[List[str]] = None


class NewEmailVerificationCode(BaseModel):
    email: EmailStr
    code: str
    creation: datetime
    expiration: datetime


class TokenInfo(BaseModel):
    access_token: str
    token_type: str


class UserAuthSchema(BaseModel):
    email: EmailStr
    auth_code: str


class UserLoginSchema(BaseModel):
    email: EmailStr
    auth_code: str


class UserAddSchema(BaseModel):
    email: EmailStr
    role: str


class UserDBSchema(BaseModel):
    email: EmailStr
    role: str
