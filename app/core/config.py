"""
Application configuration loaded from environment variables.
Production-safe defaults; override via .env or environment.
"""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation and defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False

    # Security - MUST be set in production via env
    SECRET_KEY: str = "dev-secret-change-in-production-min-32-chars"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # Database - SQLite / PostgreSQL / MySQL
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

    @property
    def is_async_database(self) -> bool:
        """True if DATABASE_URL uses an async driver."""
        return (
            "sqlite+aiosqlite" in self.DATABASE_URL
            or "postgresql+asyncpg" in self.DATABASE_URL
            or "mysql+aiomysql" in self.DATABASE_URL
        )


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance for dependency injection."""
    return Settings()
