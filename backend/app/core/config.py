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

    # Supabase Auth - Asymmetric ECC (P-256 / ES256) Configuration
    SUPABASE_URL: str = "https://placeholder.supabase.co"
    SUPABASE_JWKS_URL: str | None = None
    SUPABASE_JWT_PUBLIC_KEY: str | None = None  # Optional static public key in PEM format or JWK JSON
    SUPABASE_JWT_ALGORITHM: str = "ES256"
    SUPABASE_JWT_ALLOWED_ALGORITHMS: str = "ES256"  # Strict allowlist of permitted algorithms
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
    def allowed_jwt_algorithms_list(self) -> List[str]:
        """Strict allowlist of permitted JWT signing algorithms."""
        return [alg.strip() for alg in self.SUPABASE_JWT_ALLOWED_ALGORITHMS.split(",") if alg.strip()]

    @computed_field
    @property
    def resolved_jwks_url(self) -> str | None:
        """Derive the official Supabase JWKS endpoint if not explicitly provided."""
        if self.SUPABASE_JWKS_URL:
            return self.SUPABASE_JWKS_URL
        if self.SUPABASE_URL and not self.SUPABASE_URL.startswith("https://placeholder"):
            return f"{self.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
        return None

    @computed_field
    @property
    def is_sqlite(self) -> bool:
        return "sqlite" in self.DATABASE_URL.lower()

    @computed_field
    @property
    def async_database_url(self) -> str:
        """
        Normalize PostgreSQL connection string for SQLAlchemy asyncpg driver.
        Supabase provides 'postgresql://...' or 'postgres://...', which must
        be transformed to 'postgresql+asyncpg://...' for async SQLAlchemy execution.
        """
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        if url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


settings = Settings()
