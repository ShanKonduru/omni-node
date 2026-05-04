# OmniNode Setup and Usage Guide

## Prerequisites Checklist

- [ ] Python 3.12+ installed
- [ ] Node.js 20+ installed  
- [ ] npm installed
- [ ] Git installed (already have since project is initialized)

## Quick Setup (Recommended)

### 1. Run the Setup Script

```bash
python scripts/setup.py
```

This will:
- ✅ Check for .env file (create if missing)
- ✅ Generate secure SECRET_KEY and ENCRYPTION_KEY
- ✅ Initialize the database
- ✅ Create demo user (username: demo, password: demo123)
- ✅ Show next steps

### 2. Install Dependencies

```bash
# Backend is already installed
# Install frontend dependencies
cd frontend
npm install
```

### 3. Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 4. Access the Application

- 🌐 Frontend: http://localhost:3000
- 🔧 Backend API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs

## Manual Setup

If you prefer manual setup:

### 1. Configure Environment

```bash
cp .env.example .env
# Edit .env and set:
# - SECRET_KEY (32+ characters)
# - ENCRYPTION_KEY (32+ characters)
```

Generate keys in Python:
```python
import secrets
print(secrets.token_urlsafe(32))
```

### 2. Initialize Database

```python
python -c "from backend.core.database import init_db; init_db()"
```

### 3. Create User (Optional)

```python
from backend.core.database import SessionLocal
from backend.models.models import User
from backend.core.security import get_password_hash

db = SessionLocal()
user = User(
    username="admin",
    email="admin@example.com",
    hashed_password=get_password_hash("your-password")
)
db.add(user)
db.commit()
```

### 4. Install Frontend

```bash
cd frontend
npm install
```

## First Steps After Setup

### 1. Verify Backend is Running

```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","version":"0.1.0"}
```

### 2. Explore API Documentation

Open http://localhost:8000/docs in your browser to see:
- All available endpoints
- Request/response schemas
- Try out API calls directly

### 3. Register Your First MCP Server

#### Example: Brave Search

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
      "BRAVE_API_KEY": "your-brave-api-key"
    }
  }'
```

### 4. List Available Tools

```bash
curl http://localhost:8000/api/tools
```

### 5. Execute a Tool

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

## Troubleshooting

### Database Issues

**Problem:** Database locked
```bash
# Stop all processes, then:
rm omninode.db
python scripts/setup.py
```

### Port Already in Use

**Problem:** Port 8000 or 3000 already in use

**Solution:**
```bash
# Backend - use different port
uvicorn backend.main:app --port 8001

# Frontend - Next.js will auto-suggest port 3001
```

### Import Errors

**Problem:** Cannot import backend modules

**Solution:**
```bash
# Reinstall in editable mode
pip install -e ".[dev]"
```

### Frontend Build Issues

**Problem:** Frontend won't start

**Solution:**
```bash
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

## Development Workflow

1. **Make changes** to backend or frontend
2. **Test locally** - servers auto-reload
3. **Run tests**: `pytest tests/ -v`
4. **Commit changes**: `git commit -m "feat: description"`

## Production Deployment

⚠️ **Before deploying to production:**

1. Generate new secure keys:
```python
import secrets
print("SECRET_KEY:", secrets.token_urlsafe(32))
print("ENCRYPTION_KEY:", secrets.token_urlsafe(32))
```

2. Update `.env`:
```bash
DEBUG=False
DATABASE_URL=postgresql://user:pass@host/db  # Use PostgreSQL
CORS_ORIGINS=https://your-domain.com
```

3. Use HTTPS
4. Set up proper authentication
5. Configure rate limiting
6. Enable monitoring

## Next Steps

- 📖 Read [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Understand the system
- 🛠️ Read [DEVELOPMENT.md](docs/DEVELOPMENT.md) - Development guide
- 💡 Read [EXAMPLES.md](docs/EXAMPLES.md) - Usage examples
- 🎯 Register MCP servers and start using tools!

## Getting Help

- Check documentation in `docs/`
- Review API docs at `/docs`
- Check GitHub issues
- Review error logs in terminal

## Common Commands Reference

```bash
# Backend
cd backend
python main.py                    # Start server
uvicorn main:app --reload         # Start with auto-reload
pytest ../tests/ -v               # Run tests

# Frontend  
cd frontend
npm run dev                       # Start dev server
npm run build                     # Build for production
npm start                         # Start production server

# Database
python scripts/setup.py           # Full setup
rm omninode.db                    # Reset database

# Git
git status                        # Check status
git add .                         # Stage all
git commit -m "message"           # Commit
git log --oneline                 # View history
```

Enjoy using OmniNode! 🎉
