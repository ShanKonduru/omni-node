"""Tests for backend.services.mcp_client module."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from backend.services.mcp_client import MCPClient
from backend.models.models import MCPServer


@pytest.fixture
def stdio_server():
    """Create stdio MCP server."""
    return MCPServer(
        id=1,
        name="stdio_server",
        transport_type="stdio",
        command="python",
        args=["-m", "test_server"]
    )


@pytest.fixture
def sse_server():
    """Create SSE MCP server."""
    return MCPServer(
        id=2,
        name="sse_server",
        transport_type="sse",
        url="http://localhost:8080/sse"
    )


@pytest.mark.asyncio
async def test_discover_tools_stdio(stdio_server):
    """Test discovering tools from stdio server."""
    with patch('asyncio.create_subprocess_exec') as mock_subprocess:
        # Setup mock process
        mock_process = Mock()
        mock_process.communicate = AsyncMock(return_value=(
            b'{"tools": [{"name": "test_tool", "description": "Test", "inputSchema": {}}]}',
            b''
        ))
        mock_process.returncode = 0
        mock_subprocess.return_value = mock_process
        
        client = MCPClient()
        tools = await client.discover_tools(stdio_server)
        
        assert isinstance(tools, list)


@pytest.mark.asyncio
async def test_discover_tools_sse(sse_server):
    """Test discovering tools from SSE server."""
    with patch('httpx.AsyncClient') as mock_client:
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "tools": [{"name": "test_tool", "description": "Test", "inputSchema": {}}]
        }
        mock_response.raise_for_status = Mock()
        
        mock_async_client = Mock()
        mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
        mock_async_client.__aexit__ = AsyncMock()
        mock_async_client.post = AsyncMock(return_value=mock_response)
        
        mock_client.return_value = mock_async_client
        
        client = MCPClient()
        tools = await client.discover_tools(sse_server)
        
        assert isinstance(tools, list)


@pytest.mark.asyncio
async def test_execute_tool_stdio(stdio_server):
    """Test executing tool via stdio."""
    with patch('asyncio.create_subprocess_exec') as mock_subprocess:
        mock_process = Mock()
        mock_process.communicate = AsyncMock(return_value=(
            b'{"result": "success"}',
            b''
        ))
        mock_process.returncode = 0
        mock_subprocess.return_value = mock_process
        
        client = MCPClient()
        result = await client.execute_tool(stdio_server, "test_tool", {"arg": "value"})
        
        assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_execute_tool_sse(sse_server):
    """Test executing tool via SSE."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.json.return_value = {"result": "success"}
        mock_response.raise_for_status = Mock()
        
        mock_async_client = Mock()
        mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
        mock_async_client.__aexit__ = AsyncMock()
        mock_async_client.post = AsyncMock(return_value=mock_response)
        
        mock_client.return_value = mock_async_client
        
        client = MCPClient()
        result = await client.execute_tool(sse_server, "test_tool", {"arg": "value"})
        
        assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_execute_tool_invalid_transport():
    """Test executing tool with invalid transport type."""
    invalid_server = MCPServer(
        id=3,
        name="invalid",
        transport_type="invalid",
        command="test"
    )
    
    client = MCPClient()
    
    with pytest.raises(ValueError):
        await client.execute_tool(invalid_server, "test_tool", {})


@pytest.mark.asyncio
async def test_discover_tools_invalid_transport():
    """Test discovering tools with invalid transport type."""
    invalid_server = MCPServer(
        id=3,
        name="invalid",
        transport_type="invalid",
        command="test"
    )
    
    client = MCPClient()
    
    with pytest.raises(ValueError):
        await client.discover_tools(invalid_server)


@pytest.mark.asyncio
async def test_execute_tool_stdio_error(stdio_server):
    """Test stdio tool execution with process error."""
    with patch('asyncio.create_subprocess_exec') as mock_subprocess:
        mock_process = Mock()
        mock_process.communicate = AsyncMock(return_value=(
            b'',
            b'Error occurred'
        ))
        mock_process.returncode = 1
        mock_subprocess.return_value = mock_process
        
        client = MCPClient()
        
        with pytest.raises(Exception):
            await client.execute_tool(stdio_server, "test_tool", {})


@pytest.mark.asyncio
async def test_execute_tool_sse_error(sse_server):
    """Test SSE tool execution with HTTP error."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        
        mock_async_client = Mock()
        mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
        mock_async_client.__aexit__ = AsyncMock()
        mock_async_client.post = AsyncMock(return_value=mock_response)
        
        mock_client.return_value = mock_async_client
        
        client = MCPClient()
        
        with pytest.raises(Exception):
            await client.execute_tool(sse_server, "test_tool", {})
