from pathlib import Path

from pydantic import BaseModel

from src.config.app import BASE_DIR


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "src" / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "src" / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    expiration_timeout_minutes: int = 60
    access_cookie_name: str = "access_token_cookie"
