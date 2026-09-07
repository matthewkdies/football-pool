"""Application configuration using Pydantic BaseSettings with file/env secret fallback."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_secret(secret_name: str, env_var: str | None = None, default: str = "") -> str:
    """Read a secret from /run/secrets/{secret_name}, falling back to env var, then default.

    Args:
        secret_name: Name of the secret file under /run/secrets.
        env_var: Optional environment variable name (defaults to secret_name.upper()).
        default: Fallback string value if secret is not found.

    Returns:
        The secret value as a stripped string.
    """
    secret_path = Path(f"/run/secrets/{secret_name}")
    if secret_path.is_file():
        try:
            val = secret_path.read_text(encoding="utf-8").strip()
            if val:
                return val
        except OSError:
            pass

    target_env = env_var or secret_name.upper()
    env_val = os.getenv(target_env)
    if env_val is not None and env_val.strip():
        return env_val.strip()

    return default


class Settings(BaseSettings):
    """Global configuration settings for the football-pool application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: str = Field(default_factory=lambda: os.getenv("APP_ENV", os.getenv("FLASK_ENV", "production")))
    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG", "0") in ("1", "true", "True"))

    # Database
    db_user: str = Field(default_factory=lambda: get_secret("db_user", "POSTGRES_USER", "postgres"))
    db_pass: str = Field(default_factory=lambda: get_secret("db_pass", "POSTGRES_PASSWORD", "postgres"))
    db_host: str = Field(default_factory=lambda: os.getenv("DB_HOST", "football-pool-postgres"))
    db_port: int = Field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    db_name: str = Field(default_factory=lambda: os.getenv("DB_NAME", "football-pool"))
    database_url: str | None = Field(default_factory=lambda: os.getenv("DATABASE_URL"))

    # Security / Auth
    secret_key: str = Field(
        default_factory=lambda: get_secret(
            "secret_key",
            "APP_SECRET_KEY",
            "dev-insecure-secret-key-change-in-prod",
        )
    )
    session_cookie_name: str = "fp_session"
    session_max_age_seconds: int = 31_536_000  # 1 year

    # ESPN API & Poller
    espn_api_url: str = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    poll_interval_active_seconds: int = 60
    poll_interval_upcoming_seconds: int = 300
    poll_interval_idle_seconds: int = 900
    poll_interval_offseason_seconds: int = 3600

    # CORS & WebSocket Allowed Origins
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5600,http://127.0.0.1:5600,http://localhost:8000,http://127.0.0.1:8000",
            ).split(",")
            if origin.strip()
        ]
    )

    @property
    def async_database_url(self) -> str:
        """Constructs an async SQLAlchemy database URL."""
        if self.database_url:
            url = self.database_url
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url

        host = self.db_host
        if self.env == "development" and not host.endswith("-local") and host == "football-pool-postgres":
            host = f"{host}-local"

        user = quote_plus(self.db_user)
        pwd = quote_plus(self.db_pass)
        return f"postgresql+asyncpg://{user}:{pwd}@{host}:{self.db_port}/{self.db_name}"

    @property
    def is_production(self) -> bool:
        """Checks if current environment is production."""
        return self.env == "production"


settings = Settings()
