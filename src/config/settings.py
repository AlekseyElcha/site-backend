from pathlib import Path

from pydantic_settings import  BaseSettings, SettingsConfigDict

from src.config.app import AppConfig
from src.config.business import Business
from src.config.db import DatabaseConfig
from src.config.email import EmailServiceConfig
from src.config.jwt import AuthJWT

class Settings(BaseSettings):
    model_config = SettingsConfigDict()

    app: AppConfig = AppConfig()
    db: DatabaseConfig = DatabaseConfig()
    auth_jwt: AuthJWT = AuthJWT()
    business: Business = Business()
    email: EmailServiceConfig = EmailServiceConfig()

settings = Settings()
