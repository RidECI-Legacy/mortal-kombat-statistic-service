import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
ENV_PATH = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    APP_NAME: str = "Mortal Kombat Statistic Service"
    DEBUG: bool = False
    
    MONGO_URI: str = Field(..., validation_alias="MONGO_URI")
    MONGO_DB_NAME: str = "rideci_stats_db"
    
    REDIS_HOST: str = Field(..., validation_alias="REDIS_HOST")
    REDIS_PORT: int = 6380
    REDIS_PASSWORD: str = Field(..., validation_alias="REDIS_PASSWORD")
    GEMINI_API_KEY: str = Field(..., validation_alias="GEMINI_API_KEY")
    
    RABBITMQ_URL: str = Field(..., validation_alias="RABBITMQ_URL")

    AWS_ACCESS_KEY: str = Field(..., validation_alias="AWS_ACCESS_KEY")
    AWS_SECRET_KEY: str = Field(..., validation_alias="AWS_SECRET_KEY")
    AWS_BUCKET_NAME: str = Field(..., validation_alias="AWS_BUCKET_NAME")

    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding="utf-8")

settings = Settings()