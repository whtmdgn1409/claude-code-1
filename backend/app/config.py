"""
Application configuration using Pydantic Settings.
Loads configuration from environment variables and .env file.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database settings
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/dealmoa"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_ECHO: bool = False

    # Redis settings
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT settings
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Application settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    # CORS settings
    CORS_ORIGINS: list = ["*"]

    # Push notification settings
    FCM_SERVER_KEY: Optional[str] = None
    APNS_CERT_PATH: Optional[str] = None
    APNS_KEY_PATH: Optional[str] = None

    # Crawler settings
    CRAWLER_USER_AGENT: str = "DealMoa/1.0 (+https://dealmoa.app)"
    CRAWLER_REQUEST_DELAY: float = 1.0  # seconds between requests
    CRAWLER_MAX_RETRIES: int = 3

    # Celery settings
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    CELERY_TIMEZONE: str = "Asia/Seoul"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: list = ["json"]
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 30 * 60  # 30 minutes

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
