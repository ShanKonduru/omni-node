# OmniNode 🌐

**A Universal MCP (Model Context Protocol) Client**

OmniNode is a full-stack application that provides a unified interface to interact with multiple MCP servers through an intuitive slash-command system.

## Features

- 🔌 **Universal Server Registration**: Connect to any MCP server (stdio or SSE)
- ⚡ **Slash-Command Interface**: Autocomplete-powered CLI-style tool execution
- 🎯 **Smart Namespace Resolution**: Automatic handling of tool name conflicts
- 🔒 **Secure Configuration**: Encrypted storage of API keys and credentials
- 🚀 **Dynamic Tool Discovery**: Real-time tool and resource enumeration
- 📊 **Tool Cache**: Instant UI rendering with background sync

## Architecture

- **Frontend**: Next.js 15 (App Router) with TypeScript
- **Backend**: FastAPI with Python 3.12+
- **Database**: SQLite with SQLAlchemy ORM
- **MCP Integration**: Native MCP protocol support

## Project Structure

```
omni-node/
├── backend/              # FastAPI application
│   ├── api/             # API routes
│   ├── core/            # Core configuration
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   └── main.py          # Application entry point
├── frontend/            # Next.js application
│   ├── app/            # App Router pages
│   ├── components/     # React components
│   └── lib/            # Utilities
├── tests/              # Test suite
└── docs/               # Documentation
```

## Quick Start

### 🚀 One-Click Launch (Recommended)

**Windows:**
```bash
start.bat
```

**Linux/macOS:**
```bash
chmod +x start.sh
./start.sh
```

This will automatically:
- ✅ Run setup and initialize database
- ✅ Install all dependencies
- ✅ Start backend server (http://localhost:8000)
- ✅ Start frontend server (http://localhost:3000)

### ⚡ Quick Launch (Already Configured)

If you've already run setup before:

**Windows:**
```bash
start-quick.bat
```

**Linux/macOS:**
```bash
chmod +x start-quick.sh
./start-quick.sh
```

### 📝 Manual Setup

If you prefer manual control:

#### 1. Backend Setup

```bash
# Install Python dependencies
pip install -e ".[dev]"

# Run setup script
python scripts/setup.py

# Start the FastAPI backend
cd backend
python main.py
```

Backend will be available at http://localhost:8000
API docs at http://localhost:8000/docs

#### 2. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install Node dependencies
npm install

# Run the Next.js development server
npm run dev
```

Frontend will be available at http://localhost:3000

## Usage

### Registering an MCP Server

```python
# Example: Register a stdio-based MCP server
POST /api/servers
{
  "name": "brave-search",
  "description": "Brave Search MCP Server",
  "transport_type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-brave-search"],
  "env": {
    "BRAVE_API_KEY": "your-api-key-here"
  }
}
```

### Using Slash Commands

1. Type `/` in the command interface
2. See autocomplete suggestions for all available tools
3. For unique tools: `/tool_name`
4. For ambiguous tools: `/server.tool_name`

Example:
```bash
/brave.google_search {"query": "MCP protocol"}
```

## Architecture Deep Dive

### Namespace Resolution

OmniNode automatically handles tool name conflicts:

- **Unique tool names**: Use simple syntax `/tool_name`
- **Conflicting names**: Requires fully qualified `/server.tool_name`
- **Autocomplete**: Shows all available tools with disambiguation info

### Database Schema

```
Users → MCPServers → ToolCache
                   → ResourceCache
        
Users → ToolExecutions
```

### Security

- Environment variables encrypted at rest using Fernet
- JWT-based authentication (to be implemented)
- CORS protection
- Input validation with Pydantic

## API Endpoints

### Server Management

- `POST /api/servers` - Register new MCP server
- `GET /api/servers` - List all servers
- `GET /api/servers/{id}` - Get server details
- `PUT /api/servers/{id}` - Update server
- `DELETE /api/servers/{id}` - Remove server
- `POST /api/servers/{id}/refresh` - Refresh tool cache

### Tool Execution

- `GET /api/tools` - List all available tools
- `GET /api/tools/autocomplete?prefix=` - Get autocomplete suggestions
- `POST /api/tools/execute` - Execute a tool
- `GET /api/tools/history` - Get execution history

## Development

### Running Tests

```bash
pytest tests/ -v --cov=backend
```

### Code Quality

```bash
# Format code
black backend/ src/

# Type checking
mypy backend/

# Linting
pylint backend/
```

## Project Structure Detail

```
omni-node/
├── backend/
│   ├── api/
│   │   ├── servers.py        # Server management endpoints
│   │   └── tools.py          # Tool execution endpoints
│   ├── core/
│   │   ├── config.py         # App configuration
│   │   ├── database.py       # DB setup
│   │   └── security.py       # Auth & encryption
│   ├── models/
│   │   └── models.py         # SQLAlchemy models
│   ├── schemas/
│   │   └── schemas.py        # Pydantic schemas
│   ├── services/
│   │   ├── namespace_resolver.py  # Tool path resolution
│   │   └── mcp_client.py          # MCP communication
│   └── main.py               # FastAPI app
├── frontend/
│   ├── app/
│   │   ├── layout.tsx        # Root layout
│   │   ├── page.tsx          # Home page
│   │   └── globals.css       # Global styles
│   ├── components/           # React components
│   ├── lib/
│   │   └── api.ts            # API client
│   └── package.json
├── src/omni_node/           # Python package
├── tests/                   # Test suite
└── docs/                    # Documentation
```

## Roadmap

- [ ] Complete JWT authentication
- [ ] WebSocket support for real-time updates
- [ ] Tool execution UI with dynamic form generation
- [ ] Resource browser
- [ ] Multi-user support
- [ ] Tool execution history visualization
- [ ] Server health monitoring
- [ ] Export/import server configurations
- [ ] Plugin system for custom transports

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT
