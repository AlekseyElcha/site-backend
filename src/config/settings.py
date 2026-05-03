from pydantic_settings import  BaseSettings, SettingsConfigDict

from src.config.app_config import AppConfig
from src.config.business_config import Business
from src.config.db_config import DatabaseConfig
from src.config.email_config import EmailServiceConfig
from src.config.jwt_config import AuthJWT
from src.config.logs_config import LoggingConfig
from src.config.redis_config import RedisConfig
from src.config.s3_config import S3Settings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

    app: AppConfig = AppConfig()
    db: DatabaseConfig = DatabaseConfig()
    auth_jwt: AuthJWT = AuthJWT()
    business: Business = Business()
    email: EmailServiceConfig = EmailServiceConfig()
    s3: S3Settings = S3Settings()
    logs: LoggingConfig = LoggingConfig()
    redis: RedisConfig = RedisConfig()

settings = Settings()
