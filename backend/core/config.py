"""Application configuration using Pydantic settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # App Info
    app_name: str = "OmniNode"
    app_version: str = "0.1.0"
    debug: bool = True
    
    # Database
    database_url: str = "sqlite:///./omninode.db"
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    encryption_key: str = "your-encryption-key-here-change-in-production"
    
    # CORS
    cors_origins: str = "http://localhost:3000"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    def get_cors_origins_list(self) -> List[str]:
        """Parse CORS origins as a list from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
