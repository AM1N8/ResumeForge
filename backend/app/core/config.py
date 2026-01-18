"""
Core configuration module using Pydantic Settings.
Loads all configuration from environment variables with validation.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Groq LLM Configuration
    groq_api_key: str
    groq_model: str = "llama-3.1-70b-versatile"
    groq_temperature: float = 0.1
    groq_max_tokens: int = 4096

    # GitHub Configuration
    github_token: str = ""

    # Database Configuration
    database_url: str = "sqlite+aiosqlite:///./resume_agent.db"

    # Application Configuration
    debug: bool = False
    log_level: str = "INFO"
    max_upload_size_mb: int = 10
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def max_upload_size_bytes(self) -> int:
        """Convert MB to bytes for file size validation."""
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated origins into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache for singleton pattern - settings are loaded once.
    """
    return Settings()
