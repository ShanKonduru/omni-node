# OmniNode Development Guide

## Setting Up Your Development Environment

### Prerequisites
- Python 3.12+
- Node.js 20+
- npm or pnpm
- Git

### Initial Setup

1. **Clone and setup Python environment**
```bash
cd c:\MyProjects\omni-node
pip install -e ".[dev]"
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your secrets
```

3. **Setup frontend**
```bash
cd frontend
npm install
```

## Running the Application

### Backend
```bash
cd backend
python main.py
# Or with auto-reload:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run dev
```

## Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Backend changes: `backend/`
- Frontend changes: `frontend/`
- Tests: `tests/`

### 3. Run Tests
```bash
# Python tests
pytest tests/ -v --cov=backend

# Frontend tests (when added)
cd frontend
npm test
```

### 4. Code Quality
```bash
# Format
black backend/ src/

# Type check
mypy backend/

# Lint
pylint backend/
```

### 5. Commit and Push
```bash
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature-name
```

## Project Structure

```
omni-node/
├── backend/               # FastAPI backend
│   ├── api/              # API route handlers
│   ├── core/             # Core config, DB, security
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── main.py           # App entry point
├── frontend/             # Next.js frontend
│   ├── app/             # App Router pages
│   ├── components/      # React components
│   └── lib/             # Utilities
├── src/omni_node/       # Python package
├── tests/               # Test suite
└── docs/                # Documentation
```

## Common Development Tasks

### Adding a New API Endpoint

1. **Create route handler** in `backend/api/`
```python
@router.post("/endpoint")
async def new_endpoint(data: Schema, db: Session = Depends(get_db)):
    # Implementation
    pass
```

2. **Add schema** in `backend/schemas/schemas.py`
```python
class NewSchema(BaseModel):
    field: str
```

3. **Update frontend** in `frontend/lib/api.ts`
```typescript
export const newApi = {
  create: (data: any) => api.post('/endpoint', data),
}
```

### Adding a Database Model

1. **Define model** in `backend/models/models.py`
```python
class NewModel(Base):
    __tablename__ = "new_table"
    id = Column(Integer, primary_key=True)
    # ... fields
```

2. **Create migration** (manual for now)
```python
# Run once to create tables
from backend.core.database import init_db
init_db()
```

3. **Add queries** in appropriate service

### Adding a Frontend Component

1. **Create component** in `frontend/components/`
```typescript
export default function NewComponent() {
  return <div>Component</div>
}
```

2. **Use in page** `frontend/app/page.tsx`

## Testing

### Backend Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_namespace_resolver.py

# With coverage
pytest --cov=backend --cov-report=html

# View coverage
open htmlcov/index.html
```

### Test Structure
```python
def test_namespace_resolution():
    """Test tool name resolution."""
    # Arrange
    resolver = NamespaceResolver(db, user_id=1)
    
    # Act
    tool, server = resolver.resolve_tool("/unique_tool")
    
    # Assert
    assert tool.name == "unique_tool"
```

## Debugging

### Backend Debugging
```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use VS Code debugger with launch.json
```

### Frontend Debugging
- Use React DevTools
- Console.log()
- VS Code debugger for Next.js

## Database Management

### View Database
```bash
# SQLite browser
sqlite3 omninode.db
.tables
.schema users
SELECT * FROM users;
```

### Reset Database
```bash
rm omninode.db
python -c "from backend.core.database import init_db; init_db()"
```

## API Documentation

FastAPI auto-generates docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

Required in `.env`:
```bash
SECRET_KEY=               # JWT signing key (32+ chars)
ENCRYPTION_KEY=           # Fernet encryption key (32+ chars)
DATABASE_URL=             # Database connection string
CORS_ORIGINS=             # Allowed frontend origins
```

## Common Issues

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Change port
uvicorn main:app --port 8001
```

### Database Locked
```bash
# Stop all backend processes
# Delete database and reinitialize
rm omninode.db
python -c "from backend.core.database import init_db; init_db()"
```

### Frontend Build Issues
```bash
# Clear cache
cd frontend
rm -rf .next node_modules
npm install
npm run dev
```

## Performance Tips

### Backend
- Use `async/await` for I/O operations
- Index frequently queried columns
- Use connection pooling for production

### Frontend
- Use React.memo for expensive components
- Implement proper loading states
- Use React Query for caching

## Security Best Practices

1. Never commit `.env` files
2. Always validate user input
3. Use parameterized queries
4. Encrypt sensitive data
5. Implement rate limiting
6. Use HTTPS in production

## Getting Help

- Check [ARCHITECTURE.md](ARCHITECTURE.md)
- Review API docs at `/docs`
- Search existing issues
- Ask in discussions

## Next Steps

1. Implement JWT authentication
2. Add WebSocket support
3. Create dynamic form generator
4. Build server management UI
5. Add execution visualization
