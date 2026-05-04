"""Tests for backend.services.namespace_resolver module."""

import pytest
from unittest.mock import Mock
from backend.services.namespace_resolver import (
    NamespaceResolver,
    AmbiguityError,
    ToolNotFoundError
)
from backend.models.models import ToolCache, MCPServer


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return Mock()


@pytest.fixture
def sample_server():
    """Create sample MCP server."""
    server = MCPServer(
        id=1,
        name="test_server",
        transport_type="stdio",
        command="python",
        args=["-m", "test"]
    )
    return server


@pytest.fixture
def sample_tool():
    """Create sample tool."""
    tool = ToolCache(
        id=1,
        server_id=1,
        name="test_tool",
        description="Test tool",
        input_schema={}
    )
    return tool


def test_resolve_tool_qualified_path(mock_db, sample_server, sample_tool):
    """Test resolving tool with qualified path (server.tool)."""
    # Setup mock
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = sample_server
    mock_db.query.return_value = mock_query
    
    mock_tool_query = Mock()
    mock_tool_query.filter.return_value.filter.return_value.first.return_value = sample_tool
    mock_db.query.side_effect = [mock_query, mock_tool_query]
    
    resolver = NamespaceResolver(mock_db)
    tool, server = resolver.resolve_tool("test_server.test_tool")
    
    assert tool == sample_tool
    assert server == sample_server


def test_resolve_tool_simple_path_unique(mock_db, sample_tool, sample_server):
    """Test resolving tool with simple name when unique."""
    # Setup mock for unique tool
    mock_query = Mock()
    mock_query.filter.return_value.all.return_value = [sample_tool]
    mock_query.filter.return_value.first.return_value = sample_server
    mock_db.query.return_value = mock_query
    
    resolver = NamespaceResolver(mock_db)
    tool, server = resolver.resolve_tool("test_tool")
    
    assert tool == sample_tool


def test_resolve_tool_not_found_qualified(mock_db):
    """Test resolving non-existent tool with qualified path."""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = None
    mock_db.query.return_value = mock_query
    
    resolver = NamespaceResolver(mock_db)
    
    with pytest.raises(ToolNotFoundError):
        resolver.resolve_tool("nonexistent_server.nonexistent_tool")


def test_resolve_tool_not_found_simple(mock_db):
    """Test resolving non-existent tool with simple name."""
    mock_query = Mock()
    mock_query.filter.return_value.all.return_value = []
    mock_db.query.return_value = mock_query
    
    resolver = NamespaceResolver(mock_db)
    
    with pytest.raises(ToolNotFoundError):
        resolver.resolve_tool("nonexistent_tool")


def test_resolve_tool_ambiguous(mock_db, sample_tool):
    """Test resolving ambiguous tool name."""
    tool2 = ToolCache(
        id=2,
        server_id=2,
        name="test_tool",
        description="Another test tool",
        input_schema={}
    )
    
    mock_query = Mock()
    mock_query.filter.return_value.all.return_value = [sample_tool, tool2]
    mock_db.query.return_value = mock_query
    
    resolver = NamespaceResolver(mock_db)
    
    with pytest.raises(AmbiguityError):
        resolver.resolve_tool("test_tool")


def test_ambiguity_error():
    """Test AmbiguityError exception."""
    error = AmbiguityError("test_tool", ["server1.test_tool", "server2.test_tool"])
    assert "test_tool" in str(error)
    assert "server1.test_tool" in str(error)


def test_tool_not_found_error():
    """Test ToolNotFoundError exception."""
    error = ToolNotFoundError("nonexistent_tool")
    assert "nonexistent_tool" in str(error)


def test_resolve_tool_server_not_found(mock_db, sample_tool):
    """Test when tool exists but server is missing."""
    # Tool exists but server query returns None
    mock_tool_query = Mock()
    mock_tool_query.filter.return_value.all.return_value = [sample_tool]
    
    mock_server_query = Mock()
    mock_server_query.filter.return_value.first.return_value = None
    
    mock_db.query.side_effect = [mock_tool_query, mock_server_query]
    
    resolver = NamespaceResolver(mock_db)
    
    with pytest.raises(ToolNotFoundError):
        resolver.resolve_tool("test_tool")


def test_resolve_qualified_path_tool_not_found(mock_db, sample_server):
    """Test qualified path when server exists but tool doesn't."""
    # Server exists
    mock_server_query = Mock()
    mock_server_query.filter.return_value.first.return_value = sample_server
    
    # Tool doesn't exist
    mock_tool_query = Mock()
    mock_tool_query.filter.return_value.filter.return_value.first.return_value = None
    
    mock_db.query.side_effect = [mock_server_query, mock_tool_query]
    
    resolver = NamespaceResolver(mock_db)
    
    with pytest.raises(ToolNotFoundError):
        resolver.resolve_tool("test_server.nonexistent_tool")
