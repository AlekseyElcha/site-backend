from pydantic_settings import  BaseSettings, SettingsConfigDict

from src.config.app import AppConfig
from src.config.db import DatabaseConfig


class Settings(BaseSettings):
    model_config = SettingsConfigDict()

    app: AppConfig = AppConfig()
    db: DatabaseConfig = DatabaseConfig()

settings = Settings()
