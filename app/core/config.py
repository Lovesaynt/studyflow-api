"""Application configuration using Pydantic Settings."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "StudyFlow API"
    APP_ENV: str = "development"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://studyflow:studyflow_dev@localhost:5432/studyflow",
        description="PostgreSQL connection URL",
    )

    # JWT
    JWT_SECRET_KEY: str = Field(
        default="replace_with_a_secure_random_secret",
        description="Secret key for JWT token signing",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Security
    BCRYPT_ROUNDS: int = 12

    # CORS
    CORS_ORIGINS: list[str] = Field(
        default_factory=list,
        description="List of allowed CORS origins",
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
