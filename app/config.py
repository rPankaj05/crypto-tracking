from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings and configuration"""

    # Application
    APP_NAME: str = "Crypto Market Alert & Portfolio Tracker"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./crypto_tracker.db"

    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Price Simulation
    PRICE_UPDATE_INTERVAL: int = 5  # seconds
    PRICE_VARIATION_MIN: float = 0.5  # percent
    PRICE_VARIATION_MAX: float = 2.0  # percent

    # CORS
    CORS_ORIGINS: List[str] = ["*"]  # Allow all origins for easy deployment and sharing

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
