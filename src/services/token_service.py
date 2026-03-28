from datetime import datetime, timedelta

import jwt
from fastapi import Depends, Request, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from exceptions import DecodeTokenError, NotAdmin
from src.config.settings import settings

encoded_jwt = jwt.encode({"some": "payload"}, "secret", algorithm="HS256")
jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
):
    encoded = jwt.encode(payload, private_key, algorithm=algorithm)
    return encoded

def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
):
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded


def create_access_token(user_email: str, user_role: str,):
    jwt_payload = {
        "type": "access",
        "sub": user_email.lower(),
        "role": user_role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow()
        + timedelta(minutes=settings.auth_jwt.access_expiration_timeout_minutes),
    }
    return encode_jwt(jwt_payload)


def create_refresh_token(user_email: str, user_role: str):
    jwt_payload = {
        "type": "refresh",
        "sub": user_email.lower(),
        "role": user_role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=settings.auth_jwt.refresh_expiration_minutes),
    }
    return encode_jwt(jwt_payload)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login/",
)

def get_current_token_payload(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_jwt(
            token=token,
        )
        return payload
    except:
        raise DecodeTokenError


# def get_current_user_email_from_token(token: str):
#     try:
#         payload = jwt.decode(
#             token=token,
#             key=settings.auth_jwt.private_key_path,
#             algorithms=settings.auth_jwt.algorithm,
#         )
#         return payload.get("email")
#     except:
#         raise DecodeTokenError


# def get_current_user_role_from_token(token: str):
#     try:
#         payload = jwt.decode(
#             token=token,
#             key=settings.auth_jwt.private_key_path,
#             algorithms=settings.auth_jwt.algorithm,
#         )
#         return payload.get("role")
#     except:
#         raise DecodeTokenError


def check_admin(request: Request):
    token = request.cookies.get(settings.auth_jwt.access_cookie_name)
    try:
        payload = get_current_token_payload(token=token)
    except:
        raise DecodeTokenError
    if payload.get("role") == "admin":
        return True
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступно только администраторам."
        )


def get_current_user(request: Request):
    token = request.cookies.get(settings.auth_jwt.access_cookie_name)
    try:
        payload = get_current_token_payload(token=token)
        return payload
    except:
        raise DecodeTokenError