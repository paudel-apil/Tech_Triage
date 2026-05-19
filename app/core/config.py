from pydantic_settings import BaseSettings, SettingsConfigDict
from decouple import config
from sqlalchemy.ext.declarative import declarative_base

SECRET_KEY = config('SECRET_KEY')

class Settings(BaseSettings):
    """
    Application settings configuration class.

    This uses Pydantic's BaseSettings to automatically read
    environment variables and validate their types
    """
    PROJECT_NAME: str = 'Technical Support Ticket Platform'
    DATABASE_URL: str = config('DATABASE_URL')
    QDRANT_URL: str = config('QDRANT_URL')
    QDRANT_API_KEY: str = config('QDRANT_API_KEY')
    GROQ_API_KEY: str = config('GROQ_API_KEY')

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra = "ignore"
    )

settings = Settings()
Base = declarative_base()