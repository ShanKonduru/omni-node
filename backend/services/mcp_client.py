"""MCP client service for communicating with MCP servers."""

import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import subprocess
import httpx

from backend.models.models import MCPServer, ToolCache, ResourceCache
from backend.core.security import decrypt_env_vars


class MCPClient:
    """
    Client for communicating with MCP servers via stdio or SSE.
    
    Handles:
    - Tool discovery (tools/list)
    - Resource discovery (resources/list)
    - Tool execution (tools/call)
    """
    
    def __init__(self, server: MCPServer):
        self.server = server
        self.env_vars = self._get_env_vars()
    
    def _get_env_vars(self) -> Dict[str, str]:
        """Decrypt and return environment variables."""
        if not self.server.env_encrypted:
            return {}
        try:
            decrypted = decrypt_env_vars(self.server.env_encrypted)
            return json.loads(decrypted)
        except Exception as e:
            print(f"Error decrypting env vars: {e}")
            return {}
    
    async def discover_tools(self, db: Session) -> List[Dict[str, Any]]:
        """
        Discover tools from the MCP server.
        
        Returns:
            List of tool definitions
        """
        if self.server.transport_type == "stdio":
            return await self._discover_tools_stdio()
        elif self.server.transport_type == "sse":
            return await self._discover_tools_sse()
        else:
            raise ValueError(f"Unsupported transport type: {self.server.transport_type}")
    
    async def _discover_tools_stdio(self) -> List[Dict[str, Any]]:
        """Discover tools via stdio transport."""
        try:
            # Build command
            cmd = [self.server.command] + (self.server.args or [])
            
            # Prepare request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**self.env_vars}
            )
            
            # Send request
            stdout, stderr = await process.communicate(
                input=json.dumps(request).encode()
            )
            
            if process.returncode != 0:
                raise RuntimeError(f"Process failed: {stderr.decode()}")
            
            # Parse response
            response = json.loads(stdout.decode())
            return response.get("result", {}).get("tools", [])
            
        except Exception as e:
            print(f"Error discovering tools via stdio: {e}")
            return []
    
    async def _discover_tools_sse(self) -> List[Dict[str, Any]]:
        """Discover tools via SSE transport."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.server.url}/tools/list",
                    json={},
                    headers=self._get_auth_headers()
                )
                response.raise_for_status()
                result = response.json()
                return result.get("tools", [])
        except Exception as e:
            print(f"Error discovering tools via SSE: {e}")
            return []
    
    async def discover_resources(self) -> List[Dict[str, Any]]:
        """Discover resources from the MCP server."""
        if self.server.transport_type == "stdio":
            return await self._discover_resources_stdio()
        elif self.server.transport_type == "sse":
            return await self._discover_resources_sse()
        else:
            raise ValueError(f"Unsupported transport type: {self.server.transport_type}")
    
    async def _discover_resources_stdio(self) -> List[Dict[str, Any]]:
        """Discover resources via stdio transport."""
        try:
            cmd = [self.server.command] + (self.server.args or [])
            
            request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "resources/list",
                "params": {}
            }
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**self.env_vars}
            )
            
            stdout, stderr = await process.communicate(
                input=json.dumps(request).encode()
            )
            
            if process.returncode != 0:
                raise RuntimeError(f"Process failed: {stderr.decode()}")
            
            response = json.loads(stdout.decode())
            return response.get("result", {}).get("resources", [])
            
        except Exception as e:
            print(f"Error discovering resources via stdio: {e}")
            return []
    
    async def _discover_resources_sse(self) -> List[Dict[str, Any]]:
        """Discover resources via SSE transport."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.server.url}/resources/list",
                    json={},
                    headers=self._get_auth_headers()
                )
                response.raise_for_status()
                result = response.json()
                return result.get("resources", [])
        except Exception as e:
            print(f"Error discovering resources via SSE: {e}")
            return []
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool on the MCP server."""
        if self.server.transport_type == "stdio":
            return await self._execute_tool_stdio(tool_name, params)
        elif self.server.transport_type == "sse":
            return await self._execute_tool_sse(tool_name, params)
        else:
            raise ValueError(f"Unsupported transport type: {self.server.transport_type}")
    
    async def _execute_tool_stdio(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool via stdio transport."""
        try:
            cmd = [self.server.command] + (self.server.args or [])
            
            request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": params
                }
            }
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**self.env_vars}
            )
            
            stdout, stderr = await process.communicate(
                input=json.dumps(request).encode()
            )
            
            if process.returncode != 0:
                return {
                    "error": f"Process failed: {stderr.decode()}"
                }
            
            response = json.loads(stdout.decode())
            return response.get("result", {})
            
        except Exception as e:
            return {
                "error": f"Error executing tool: {str(e)}"
            }
    
    async def _execute_tool_sse(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool via SSE transport."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.server.url}/tools/call",
                    json={
                        "name": tool_name,
                        "arguments": params
                    },
                    headers=self._get_auth_headers()
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {
                "error": f"Error executing tool: {str(e)}"
            }
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for SSE requests."""
        headers = {}
        # Add API keys from env vars if needed
        for key, value in self.env_vars.items():
            if key.startswith("API_") or key.endswith("_KEY"):
                headers[key] = value
        return headers


async def update_tool_cache(db: Session, server: MCPServer):
    """
    Update the tool cache for a given server.
    
    Args:
        db: Database session
        server: MCP server instance
    """
    client = MCPClient(server)
    
    # Discover tools
    tools = await client.discover_tools(db)
    
    # Clear old cache for this server
    db.query(ToolCache).filter(ToolCache.server_id == server.id).delete()
    
    # Insert new tools
    for tool_data in tools:
        tool = ToolCache(
            server_id=server.id,
            name=tool_data.get("name"),
            description=tool_data.get("description"),
            input_schema=tool_data.get("inputSchema"),
            last_discovered=datetime.utcnow()
        )
        db.add(tool)
    
    db.commit()


async def update_resource_cache(db: Session, server: MCPServer):
    """
    Update the resource cache for a given server.
    
    Args:
        db: Database session
        server: MCP server instance
    """
    client = MCPClient(server)
    
    # Discover resources
    resources = await client.discover_resources()
    
    # Clear old cache for this server
    db.query(ResourceCache).filter(ResourceCache.server_id == server.id).delete()
    
    # Insert new resources
    for resource_data in resources:
        resource = ResourceCache(
            server_id=server.id,
            uri=resource_data.get("uri"),
            name=resource_data.get("name"),
            description=resource_data.get("description"),
            mime_type=resource_data.get("mimeType"),
            last_discovered=datetime.utcnow()
        )
        db.add(resource)
    
    db.commit()
