from pathlib import Path

from pydantic_settings import  BaseSettings, SettingsConfigDict

from src.config.app import AppConfig
from src.config.db import DatabaseConfig

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict()

    app: AppConfig = AppConfig()
    db: DatabaseConfig = DatabaseConfig()
    auth_jwt = AuthJWT = AuthJWT()

settings = Settings()
