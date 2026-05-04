# OmniNode - Quick Start Examples

## Example 1: Register a Brave Search Server

```bash
curl -X POST http://localhost:8000/api/servers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "brave-search",
    "description": "Brave Search MCP Server",
    "transport_type": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-brave-search"],
    "env": {
      "BRAVE_API_KEY": "your-brave-api-key-here"
    }
  }'
```

## Example 2: List All Servers

```bash
curl http://localhost:8000/api/servers
```

## Example 3: Get Autocomplete Suggestions

```bash
curl http://localhost:8000/api/tools/autocomplete?prefix=search
```

## Example 4: Execute a Tool

```bash
curl -X POST http://localhost:8000/api/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_path": "/brave.google_search",
    "params": {
      "query": "Model Context Protocol"
    }
  }'
```

## Example 5: View Execution History

```bash
curl http://localhost:8000/api/tools/history?limit=10
```

## Example 6: Register an SSE-based Server

```bash
curl -X POST http://localhost:8000/api/servers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "custom-sse",
    "description": "Custom SSE MCP Server",
    "transport_type": "sse",
    "url": "https://your-server.com/mcp",
    "env": {
      "API_KEY": "your-api-key"
    }
  }'
```

## Example 7: Refresh Server Cache

```bash
curl -X POST http://localhost:8000/api/servers/1/refresh
```

## Example 8: Python Client Usage

```python
import asyncio
from backend.services.namespace_resolver import NamespaceResolver
from backend.services.mcp_client import MCPClient
from backend.core.database import SessionLocal
from backend.models.models import MCPServer

async def main():
    db = SessionLocal()
    
    # Get resolver
    resolver = NamespaceResolver(db, user_id=1)
    
    # Get all tools
    tools = resolver.get_all_tools()
    print(f"Found {len(tools)} tools")
    
    # Resolve a tool
    try:
        tool, server = resolver.resolve_tool("/google_search")
        print(f"Tool: {tool.name} on server: {server.name}")
        
        # Execute it
        client = MCPClient(server)
        result = await client.execute_tool(
            tool.name,
            {"query": "test"}
        )
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    db.close()

asyncio.run(main())
```

## Example 9: Testing Namespace Resolution

```python
# Test ambiguity detection
from backend.services.namespace_resolver import NamespaceResolver, AmbiguityError

resolver = NamespaceResolver(db, user_id=1)

try:
    # This will fail if multiple servers have "search"
    tool, server = resolver.resolve_tool("/search")
except AmbiguityError as e:
    print(f"Tool is ambiguous. Available on: {e.servers}")
    print(f"Use one of: {[f'/{s}.search' for s in e.servers]}")

# Use fully qualified name
tool, server = resolver.resolve_tool("/brave.search")
```

## Example 10: Complete Workflow

```python
import asyncio
from backend.core.database import SessionLocal
from backend.models.models import MCPServer
from backend.services.mcp_client import update_tool_cache, MCPClient
from backend.core.security import encrypt_env_vars
import json

async def setup_and_use_server():
    db = SessionLocal()
    
    # 1. Create server
    env_json = json.dumps({"API_KEY": "secret"})
    server = MCPServer(
        user_id=1,
        name="my-server",
        transport_type="stdio",
        command="npx",
        args=["-y", "some-mcp-server"],
        env_encrypted=encrypt_env_vars(env_json)
    )
    db.add(server)
    db.commit()
    db.refresh(server)
    
    # 2. Discover tools
    await update_tool_cache(db, server)
    
    # 3. List discovered tools
    from backend.services.namespace_resolver import NamespaceResolver
    resolver = NamespaceResolver(db, user_id=1)
    tools = resolver.get_all_tools()
    
    print(f"Server '{server.name}' has {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # 4. Execute a tool
    if tools:
        tool = tools[0]
        client = MCPClient(server)
        result = await client.execute_tool(tool.name, {})
        print(f"Execution result: {result}")
    
    db.close()

asyncio.run(setup_and_use_server())
```
