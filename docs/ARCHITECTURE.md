# OmniNode - Technical Architecture

## System Overview

OmniNode is a full-stack universal MCP (Model Context Protocol) client that provides a unified interface to interact with multiple MCP servers through an intuitive slash-command system.

## Core Components

### 1. Backend (FastAPI + Python)

#### Namespace Resolver
The heart of OmniNode's intelligence. Handles:
- **Simple Resolution**: `/tool_name` for unique tools
- **Qualified Resolution**: `/server.tool_name` for disambiguation
- **Ambiguity Detection**: Automatically detects naming conflicts
- **Autocomplete**: Provides intelligent suggestions

```python
# Example usage
resolver = NamespaceResolver(db, user_id)
tool, server = resolver.resolve_tool("/google_search")
# Returns the tool and server if unique
# Raises AmbiguityError if multiple servers have this tool
```

#### MCP Client Service
Abstracts transport layer differences:
- **Stdio Transport**: Spawns subprocess, communicates via JSON-RPC
- **SSE Transport**: HTTP-based server-sent events
- **Unified Interface**: Same API regardless of transport

```python
client = MCPClient(server)
tools = await client.discover_tools(db)
result = await client.execute_tool("search", {"query": "test"})
```

#### Database Models
Optimized schema for performance:
- **Users**: Authentication and session management
- **MCPServers**: Server configurations with encrypted env vars
- **ToolCache**: Local snapshot for instant autocomplete
- **ResourceCache**: Available resources from servers
- **ToolExecutions**: Complete execution history

### 2. Frontend (Next.js 15 + React)

#### Command Interface
- Slash-command style input
- Real-time autocomplete
- Visual disambiguation
- Execution history

#### Features (Planned)
- Dynamic form generation from JSON Schema
- WebSocket for real-time updates
- Server management UI
- Execution visualization

## Data Flow

### 1. Server Registration
```
User → Frontend → API → Database
                  ↓
            MCP Server (discover tools)
                  ↓
            Tool Cache (store)
```

### 2. Tool Execution
```
User types: /google_search
     ↓
Autocomplete suggests available tools
     ↓
User submits command
     ↓
Namespace Resolver finds exact tool
     ↓
MCP Client executes on correct server
     ↓
Result returned + saved to history
```

## Security Architecture

### Encryption at Rest
```python
# Environment variables encrypted before storage
env_json = json.dumps({"API_KEY": "secret"})
encrypted = encrypt_env_vars(env_json)
# Stored as binary in database
```

### Authentication Flow (TODO)
```
1. User login → JWT token
2. Token stored in httpOnly cookie
3. All API requests include token
4. Backend validates on each request
```

## Transport Protocols

### Stdio Transport
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

Process spawned with environment variables, JSON-RPC over stdin/stdout.

### SSE Transport
```
POST /tools/list
Headers: { Authorization: "Bearer token" }
Body: {}
```

HTTP-based communication with SSE endpoints.

## Performance Optimizations

### Tool Cache
- Tools cached locally after discovery
- Autocomplete is instant (no server round-trip)
- Background refresh every N minutes

### Database Indexing
- `users.username` - Index for fast lookups
- `mcp_servers.name` - Index for namespace resolution
- `tool_cache.name` - Index for autocomplete queries

## Extensibility

### Adding New Transports
1. Implement transport in `MCPClient`
2. Add enum value to `TransportType`
3. Update frontend wizard

### Custom Tool Handlers
```python
# Future: Plugin system
class CustomToolHandler:
    def execute(self, tool_name, params):
        # Custom logic
        pass
```

## Error Handling

### Namespace Errors
```python
try:
    resolver.resolve_tool("/search")
except AmbiguityError as e:
    # Multiple servers have this tool
    # Suggest: /brave.search or /google.search
except ToolNotFoundError as e:
    # Tool doesn't exist
```

### Execution Errors
All execution errors logged to `ToolExecutions` table with:
- Error message
- Stack trace
- Timing information
- Input parameters

## Testing Strategy

### Unit Tests
- Namespace resolver logic
- Tool cache updates
- Security functions

### Integration Tests
- Full API endpoint testing
- Database operations
- Mock MCP servers

### E2E Tests
- Frontend → Backend → Database
- Tool execution flow
- Error handling

## Deployment

### Production Checklist
- [ ] Generate secure SECRET_KEY
- [ ] Generate secure ENCRYPTION_KEY (32 bytes)
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Rate limiting

### Docker Deployment
```dockerfile
# backend/Dockerfile
FROM python:3.12
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0"]
```

## Future Enhancements

1. **Real-time Updates**: WebSocket for live tool output
2. **Collaboration**: Multi-user execution sharing
3. **Workflows**: Chain multiple tools together
4. **Monitoring**: Server health dashboards
5. **Analytics**: Usage statistics and insights
6. **Plugin System**: Custom transport implementations
7. **API Rate Limiting**: Per-user quotas
8. **Caching Layer**: Redis for performance
9. **Queue System**: Celery for background tasks
10. **Logging**: Structured logging with ELK stack
