"""
API Configuration

Settings for FastAPI server including CORS, database, and server configuration.
"""

import re

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings.

    Configuration can be overridden via environment variables prefixed with SENTINEL_.
    Example: SENTINEL_PORT=9000
    """

    # CORS - localhost only for security
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "tauri://localhost",
        "http://tauri.localhost",
    ]

    access_token: SecretStr | None = None

    @field_validator("access_token")
    @classmethod
    def validate_access_token(cls, token: SecretStr | None) -> SecretStr | None:
        if token is not None and not re.fullmatch(r"[0-9a-fA-F]{64}", token.get_secret_value()):
            raise ValueError("Provide a 64-character hexadecimal access token")
        return token

    # Database
    database_url: str = "~/.sentinel/sentinel.db"

    # Server
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = False

    # API
    api_prefix: str = "/api"

    class Config:
        env_prefix = "SENTINEL_"
        case_sensitive = False


settings = Settings()
