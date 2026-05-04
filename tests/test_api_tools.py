"""Tests for backend.api.tools module."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from backend.main import app
from backend.models.models import ToolCache, MCPServer, ToolExecution
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
def sample_tool():
    """Create sample tool."""
    return ToolCache(
        id=1,
        server_id=1,
        name="test_tool",
        description="Test tool",
        input_schema={}
    )


@pytest.fixture
def sample_server():
    """Create sample server."""
    return MCPServer(
        id=1,
        name="test_server",
        transport_type="stdio",
        command="python",
        args=["-m", "test"]
    )


def test_autocomplete(client, mock_db, sample_tool):
    """Test tool autocomplete."""
    mock_query = Mock()
    mock_query.filter.return_value.all.return_value = [sample_tool]
    
    # Mock server query
    mock_server_query = Mock()
    mock_server = Mock()
    mock_server.name = "test_server"
    mock_server_query.filter.return_value.first.return_value = mock_server
    
    mock_db.query.side_effect = [mock_query, mock_server_query]
    
    response = client.get("/api/tools/autocomplete?query=test")
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data


def test_autocomplete_empty_query(client, mock_db):
    """Test autocomplete with empty query."""
    response = client.get("/api/tools/autocomplete?query=")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_execute_tool(client, mock_db, sample_tool, sample_server):
    """Test executing a tool."""
    mock_db.add = Mock()
    mock_db.commit = Mock()
    mock_db.refresh = Mock()
    
    with patch('backend.services.namespace_resolver.NamespaceResolver') as mock_resolver_class:
        mock_resolver = Mock()
        mock_resolver.resolve_tool.return_value = (sample_tool, sample_server)
        mock_resolver_class.return_value = mock_resolver
        
        with patch('backend.services.mcp_client.MCPClient') as mock_client_class:
            mock_client = Mock()
            mock_client.execute_tool = AsyncMock(return_value={"result": "success"})
            mock_client_class.return_value = mock_client
            
            execute_data = {
                "tool_path": "test_server.test_tool",
                "params": {"arg": "value"}
            }
            
            response = client.post("/api/tools/execute", json=execute_data)
            assert response.status_code == 200


def test_get_execution_history(client, mock_db):
    """Test getting tool execution history."""
    mock_execution = Mock()
    mock_execution.id = 1
    mock_execution.tool_path = "test.tool"
    mock_execution.arguments = {}
    mock_execution.result = {}
    mock_execution.success = True
    mock_execution.executed_at = "2026-05-04T12:00:00"
    
    mock_query = Mock()
    mock_query.order_by.return_value.limit.return_value.all.return_value = [mock_execution]
    mock_db.query.return_value = mock_query
    
    response = client.get("/api/tools/history")
    assert response.status_code == 200


def test_get_execution_history_with_limit(client, mock_db):
    """Test getting execution history with limit."""
    mock_query = Mock()
    mock_query.order_by.return_value.limit.return_value.all.return_value = []
    mock_db.query.return_value = mock_query
    
    response = client.get("/api/tools/history?limit=5")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_execute_tool_not_found(client, mock_db):
    """Test executing non-existent tool."""
    with patch('backend.services.namespace_resolver.NamespaceResolver') as mock_resolver_class:
        from backend.services.namespace_resolver import ToolNotFoundError
        mock_resolver = Mock()
        mock_resolver.resolve_tool.side_effect = ToolNotFoundError("tool not found")
        mock_resolver_class.return_value = mock_resolver
        
        execute_data = {
            "tool_path": "nonexistent.tool",
            "params": {}
        }
        
        response = client.post("/api/tools/execute", json=execute_data)
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_execute_tool_ambiguous(client, mock_db):
    """Test executing ambiguous tool."""
    with patch('backend.services.namespace_resolver.NamespaceResolver') as mock_resolver_class:
        from backend.services.namespace_resolver import AmbiguityError
        mock_resolver = Mock()
        mock_resolver.resolve_tool.side_effect = AmbiguityError("tool", ["tool1", "tool2"])
        mock_resolver_class.return_value = mock_resolver
        
        execute_data = {
            "tool_path": "ambiguous_tool",
            "params": {}
        }
        
        response = client.post("/api/tools/execute", json=execute_data)
        assert response.status_code == 400
