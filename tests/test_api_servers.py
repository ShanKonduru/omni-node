"""Tests for backend.api.servers module."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from backend.main import app
from backend.models.models import MCPServer
from backend.core.database import get_db


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return Mock()


@pytest.fixture
def client(mock_db):
    """Create test client with mocked database."""
    def override_get_db():
        yield mock_db
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_server():
    """Create sample MCP server."""
    return MCPServer(
        id=1,
        name="test_server",
        transport_type="stdio",
        command="python",
        args=["-m", "test"]
    )


def test_create_server(client, mock_db):
    """Test creating an MCP server."""
    mock_db.add = Mock()
    mock_db.commit = Mock()
    mock_db.refresh = Mock()
    
    server_data = {
        "name": "test_server",
        "transport_type": "stdio",
        "command": "python",
        "args": ["-m", "test"]
    }
    
    with patch('backend.api.servers.encrypt_env_vars') as mock_encrypt:
        mock_encrypt.return_value = "encrypted"
        response = client.post("/api/servers/", json=server_data)
        
        assert response.status_code == 200


def test_list_servers(client, mock_db, sample_server):
    """Test listing all servers."""
    mock_query = Mock()
    mock_query.all.return_value = [sample_server]
    mock_db.query.return_value = mock_query
    
    response = client.get("/api/servers/")
    assert response.status_code == 200


def test_get_server(client, mock_db, sample_server):
    """Test getting a specific server."""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = sample_server
    mock_db.query.return_value = mock_query
    
    response = client.get("/api/servers/1")
    assert response.status_code == 200


def test_get_server_not_found(client, mock_db):
    """Test getting non-existent server."""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = None
    mock_db.query.return_value = mock_query
    
    response = client.get("/api/servers/999")
    assert response.status_code == 404


def test_update_server(client, mock_db, sample_server):
    """Test updating a server."""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = sample_server
    mock_db.query.return_value = mock_query
    mock_db.commit = Mock()
    mock_db.refresh = Mock()
    
    update_data = {"name": "updated_server"}
    
    with patch('backend.api.servers.encrypt_env_vars') as mock_encrypt:
        mock_encrypt.return_value = "encrypted"
        response = client.put("/api/servers/1", json=update_data)
        
        assert response.status_code == 200


def test_delete_server(client, mock_db, sample_server):
    """Test deleting a server."""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = sample_server
    mock_db.query.return_value = mock_query
    mock_db.delete = Mock()
    mock_db.commit = Mock()
    
    response = client.delete("/api/servers/1")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_refresh_tools(client, mock_db, sample_server):
    """Test refreshing server tools."""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = sample_server
    mock_db.query.return_value = mock_query
    mock_db.add = Mock()
    mock_db.commit = Mock()
    
    with patch('backend.services.mcp_client.MCPClient') as mock_client_class:
        mock_client = Mock()
        mock_client.discover_tools = AsyncMock(return_value=[
            {"name": "test_tool", "description": "Test", "inputSchema": {}}
        ])
        mock_client_class.return_value = mock_client
        
        response = client.post("/api/servers/1/refresh")
        assert response.status_code == 200
