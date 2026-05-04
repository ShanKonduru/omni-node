"""Tests for backend.main FastAPI application."""

import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_read_root(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "OmniNode" in data["message"]


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app_name" in data
    assert "version" in data


def test_cors_headers(client):
    """Test CORS headers are present."""
    response = client.options("/health")
    assert response.status_code == 200


def test_app_metadata(client):
    """Test app title and version."""
    assert app.title == "OmniNode"
    assert hasattr(app, 'version')


def test_lifespan_startup():
    """Test lifespan startup event."""
    # The app should start without errors
    with TestClient(app) as test_client:
        response = test_client.get("/health")
        assert response.status_code == 200


def test_api_routers_included():
    """Test that API routers are included."""
    routes = [route.path for route in app.routes]
    
    # Check that server and tool routes exist
    assert any("/api/servers" in route for route in routes)
    assert any("/api/tools" in route for route in routes)
