"""Tests for backend.core.config module."""

import pytest
from backend.core.config import Settings, get_settings


def test_settings_defaults():
    """Test Settings with default values."""
    settings = Settings()
    assert settings.app_name == "OmniNode"
    assert settings.app_version == "0.1.0"
    assert settings.debug is True
    assert settings.database_url == "sqlite:///./omninode.db"
    assert settings.algorithm == "HS256"
    assert settings.access_token_expire_minutes == 30


def test_settings_custom_values(monkeypatch):
    """Test Settings with custom environment variables."""
    monkeypatch.setenv("APP_NAME", "CustomApp")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
    
    settings = Settings()
    assert settings.app_name == "CustomApp"
    assert settings.debug is False
    assert settings.database_url == "sqlite:///./test.db"


def test_get_cors_origins_list_string():
    """Test CORS origins parsing from comma-separated string."""
    settings = Settings(cors_origins="http://localhost:3000,http://localhost:8080")
    origins = settings.get_cors_origins_list()
    assert origins == ["http://localhost:3000", "http://localhost:8080"]


def test_get_cors_origins_list_single():
    """Test CORS origins with single origin."""
    settings = Settings(cors_origins="http://localhost:3000")
    origins = settings.get_cors_origins_list()
    assert origins == ["http://localhost:3000"]


def test_get_cors_origins_list_with_spaces():
    """Test CORS origins parsing with spaces."""
    settings = Settings(cors_origins="http://localhost:3000, http://localhost:8080")
    origins = settings.get_cors_origins_list()
    assert origins == ["http://localhost:3000", "http://localhost:8080"]


def test_get_settings_singleton():
    """Test that get_settings returns cached instance."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2
