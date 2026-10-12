import os
from typing import List
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "vigilX"
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database: Supabase PostgreSQL URI (postgresql+asyncpg://...) or SQLite fallback
    DATABASE_URL: str = "sqlite+aiosqlite:///./vigilx_dev.db"

    # Supabase Auth
    SUPABASE_URL: str = "https://placeholder.supabase.co"
    SUPABASE_JWT_SECRET: str = "default-dev-jwt-secret-replace-in-production"
    SUPABASE_JWKS_URL: str | None = None
    SUPABASE_SERVICE_ROLE_KEY: str | None = None
    SUPABASE_STORAGE_BUCKET: str = "brand-logos"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    @computed_field
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @computed_field
    @property
    def is_sqlite(self) -> bool:
        return "sqlite" in self.DATABASE_URL.lower()

    @computed_field
    @property
    def async_database_url(self) -> str:
        """
        Normalize PostgreSQL connection string for SQLAlchemy asyncpg driver.
        Supabase often provides 'postgresql://...' or 'postgres://...', which must
        be transformed to 'postgresql+asyncpg://...' for async SQLAlchemy execution.
        """
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        if url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


settings = Settings()
