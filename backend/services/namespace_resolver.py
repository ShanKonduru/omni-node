"""Namespace resolver for handling tool path resolution and conflicts."""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from backend.models.models import ToolCache, MCPServer
from backend.schemas.schemas import ToolWithServer


class AmbiguityError(Exception):
    """Raised when a tool name is ambiguous across multiple servers."""
    
    def __init__(self, tool_name: str, servers: List[str]):
        self.tool_name = tool_name
        self.servers = servers
        super().__init__(
            f"Tool '{tool_name}' exists on multiple servers: {', '.join(servers)}. "
            f"Use /<server_name>.{tool_name} to specify which one."
        )


class ToolNotFoundError(Exception):
    """Raised when a tool is not found."""
    
    def __init__(self, tool_path: str):
        self.tool_path = tool_path
        super().__init__(f"Tool '{tool_path}' not found.")


class NamespaceResolver:
    """
    Resolves tool paths with smart namespace handling.
    
    Supports:
    - /tool_name (if unique)
    - /server_name.tool_name (fully qualified)
    """
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
    
    def resolve_tool(self, tool_path: str) -> Tuple[ToolCache, MCPServer]:
        """
        Resolve a tool path to a specific tool and server.
        
        Args:
            tool_path: The tool path (e.g., "/google_search" or "/brave.google_search")
        
        Returns:
            Tuple of (ToolCache, MCPServer)
        
        Raises:
            AmbiguityError: If tool name is ambiguous
            ToolNotFoundError: If tool is not found
        """
        # Remove leading slash
        path = tool_path.lstrip("/")
        
        # Check if fully qualified (server.tool format)
        if "." in path:
            return self._resolve_qualified_path(path)
        else:
            return self._resolve_simple_path(path)
    
    def _resolve_qualified_path(self, path: str) -> Tuple[ToolCache, MCPServer]:
        """Resolve a fully qualified path (server.tool)."""
        parts = path.split(".", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid tool path format: {path}")
        
        server_name, tool_name = parts
        
        # Find the specific tool on the specific server
        result = (
            self.db.query(ToolCache, MCPServer)
            .join(MCPServer, ToolCache.server_id == MCPServer.id)
            .filter(
                MCPServer.user_id == self.user_id,
                MCPServer.name == server_name,
                MCPServer.is_active == True,
                ToolCache.name == tool_name
            )
            .first()
        )
        
        if not result:
            raise ToolNotFoundError(f"{server_name}.{tool_name}")
        
        return result
    
    def _resolve_simple_path(self, tool_name: str) -> Tuple[ToolCache, MCPServer]:
        """Resolve a simple tool name (check for uniqueness)."""
        # Find all matching tools across all servers
        results = (
            self.db.query(ToolCache, MCPServer)
            .join(MCPServer, ToolCache.server_id == MCPServer.id)
            .filter(
                MCPServer.user_id == self.user_id,
                MCPServer.is_active == True,
                ToolCache.name == tool_name
            )
            .all()
        )
        
        if not results:
            raise ToolNotFoundError(tool_name)
        
        if len(results) > 1:
            # Multiple servers have this tool - ambiguous
            server_names = [server.name for _, server in results]
            raise AmbiguityError(tool_name, server_names)
        
        # Unique tool found
        return results[0]
    
    def get_all_tools(self, prefix: Optional[str] = None) -> List[ToolWithServer]:
        """
        Get all available tools for autocomplete.
        
        Args:
            prefix: Optional prefix to filter results
        
        Returns:
            List of tools with server information
        """
        query = (
            self.db.query(ToolCache, MCPServer)
            .join(MCPServer, ToolCache.server_id == MCPServer.id)
            .filter(
                MCPServer.user_id == self.user_id,
                MCPServer.is_active == True
            )
        )
        
        if prefix:
            # Filter by prefix (supports both simple and qualified names)
            prefix_clean = prefix.lstrip("/")
            query = query.filter(
                (ToolCache.name.like(f"{prefix_clean}%")) |
                ((MCPServer.name + "." + ToolCache.name).like(f"{prefix_clean}%"))
            )
        
        results = query.all()
        
        # Build response with fully qualified names
        tools = []
        tool_name_counts = {}
        
        # First pass: count tool name occurrences
        for tool, server in results:
            tool_name_counts[tool.name] = tool_name_counts.get(tool.name, 0) + 1
        
        # Second pass: build response with disambiguation info
        for tool, server in results:
            is_ambiguous = tool_name_counts[tool.name] > 1
            
            tools.append(ToolWithServer(
                id=tool.id,
                server_id=tool.server_id,
                name=tool.name,
                description=tool.description,
                input_schema=tool.input_schema,
                last_discovered=tool.last_discovered,
                server_name=server.name,
                fully_qualified_name=f"{server.name}.{tool.name}"
            ))
        
        return tools
    
    def check_ambiguity(self, tool_name: str) -> Tuple[bool, List[str]]:
        """
        Check if a tool name is ambiguous.
        
        Returns:
            Tuple of (is_ambiguous, list_of_server_names)
        """
        results = (
            self.db.query(MCPServer.name)
            .join(ToolCache, ToolCache.server_id == MCPServer.id)
            .filter(
                MCPServer.user_id == self.user_id,
                MCPServer.is_active == True,
                ToolCache.name == tool_name
            )
            .all()
        )
        
        server_names = [r[0] for r in results]
        return len(server_names) > 1, server_names
