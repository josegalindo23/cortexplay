"""
Application configuration using Pydantic Settings.

All environment variables are loaded from the .env file.
This pattern ensures type safety and a single source of truth
for configuration across the entire application.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    # Data paths
    DATA_DIR: str = "./data"
    PREDICTIONS_DIR: str = "./data/predictions"
    SURFACE_DIR: str = "./data/surface"
    REGIONS_DIR: str = "./data/regions"

    # TRIBE v2
    TRIBE_CACHE_DIR: str = "./cache/tribev2"
    TRIBE_MODEL_ID: str = "facebook/tribev2"

    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """Return list of allowed CORS origins."""
        return [self.FRONTEND_URL, "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton instance
settings = Settings()