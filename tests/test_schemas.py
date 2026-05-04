"""Tests for backend.schemas.schemas module."""

import pytest
from pydantic import ValidationError
from backend.schemas.schemas import (
    UserCreate,
    UserResponse,
    MCPServerCreate,
    MCPServerResponse,
    MCPServerUpdate,
    ToolExecuteRequest,
    ToolExecuteResponse,
    ToolCacheResponse,
    AutocompleteResult,
    AutocompleteResponse,
    TransportType,
)


def test_user_create_valid():
    """Test UserCreate with valid data."""
    user = UserCreate(username="testuser", email="test@example.com", password="password123")
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password == "password123"


def test_user_create_invalid_email():
    """Test UserCreate with invalid email."""
    with pytest.raises(ValidationError):
        UserCreate(username="testuser", email="invalid-email", password="password123")


def test_mcp_server_create_stdio():
    """Test MCPServerCreate for stdio transport."""
    server = MCPServerCreate(
        name="TestServer",
        transport_type="stdio",
        command="python",
        args=["-m", "server"],
        env={"KEY": "value"}
    )
    assert server.name == "TestServer"
    assert server.transport_type == TransportType.STDIO
    assert server.command == "python"


def test_mcp_server_create_sse():
    """Test MCPServerCreate for SSE transport."""
    server = MCPServerCreate(
        name="TestServer",
        transport_type="sse",
        url="http://localhost:8080/sse"
    )
    assert server.name == "TestServer"
    assert server.transport_type == TransportType.SSE
    assert server.url == "http://localhost:8080/sse"


def test_tool_execute_request():
    """Test ToolExecuteRequest."""
    request = ToolExecuteRequest(
        tool_path="server.tool_name",
        params={"arg1": "value1"}
    )
    assert request.tool_path == "server.tool_name"
    assert request.params == {"arg1": "value1"}


def test_tool_execute_response():
    """Test ToolExecuteResponse."""
    from datetime import datetime
    response = ToolExecuteResponse(
        id=1,
        tool_name="tool_name",
        server_name="server",
        status="completed",
        output={"data": "result"},
        started_at=datetime.now()
    )
    assert response.status == "completed"
    assert response.output == {"data": "result"}


def test_tool_cache_response():
    """Test ToolCacheResponse."""
    from datetime import datetime
    tool = ToolCacheResponse(
        id=1,
        server_id=1,
        name="tool_name",
        description="Test tool",
        input_schema={"type": "object"},
        last_discovered=datetime.now()
    )
    assert tool.id == 1
    assert tool.name == "tool_name"


def test_autocomplete_result():
    """Test AutocompleteResult."""
    result = AutocompleteResult(
        command="server.tool",
        description="Test tool",
        server_name="server",
        is_ambiguous=False
    )
    assert result.command == "server.tool"
    assert result.is_ambiguous is False


def test_autocomplete_response():
    """Test AutocompleteResponse."""
    result1 = AutocompleteResult(
        command="server.tool1",
        server_name="server"
    )
    result2 = AutocompleteResult(
        command="server.tool2",
        server_name="server"
    )
    response = AutocompleteResponse(
        results=[result1, result2],
        total=2
    )
    assert response.total == 2
    assert len(response.results) == 2
