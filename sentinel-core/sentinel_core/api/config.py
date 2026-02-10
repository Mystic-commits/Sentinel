"""
API Configuration

Settings for FastAPI server including CORS, database, and server configuration.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings.
    
    Configuration can be overridden via environment variables prefixed with SENTINEL_.
    Example: SENTINEL_PORT=9000
    """
    
    # CORS - localhost only for security
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "tauri://localhost",  # For Tauri desktop app
    ]
    
    # Database
    database_url: str = "~/.sentinel/sentinel.db"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # API
    api_prefix: str = "/api"
    
    class Config:
        env_prefix = "SENTINEL_"
        case_sensitive = False


settings = Settings()
