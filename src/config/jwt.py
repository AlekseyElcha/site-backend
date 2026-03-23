from pathlib import Path

from pydantic import BaseModel

from src.config.app import BASE_DIR


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "src" / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "src" / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_expiration_timeout_minutes: int = 2
    refresh_expiration_minutes: int = 30 * 60 * 24 # 30 дней
    access_cookie_name: str = "access_token_cookie"
    refresh_cookie_name: str = "refresh_token_cookie"
