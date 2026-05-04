# 🚀 OmniNode Launcher Scripts

Quick reference for the launcher scripts.

## Available Scripts

### Full Setup & Launch

**Windows:**
```bash
start.bat
```

**Linux/macOS:**
```bash
chmod +x start.sh
./start.sh
```

**What it does:**
1. ✅ Runs `python scripts/setup.py` - Initializes database, creates demo user
2. ✅ Checks and installs frontend dependencies (`npm install`)
3. ✅ Starts backend server in new terminal/process
4. ✅ Starts frontend server in new terminal/process

**Use when:**
- First time running the project
- After pulling updates that might need setup
- When dependencies might have changed

---

### Quick Launch (Skip Setup)

**Windows:**
```bash
start-quick.bat
```

**Linux/macOS:**
```bash
chmod +x start-quick.sh
./start-quick.sh
```

**What it does:**
1. ✅ Starts backend server immediately
2. ✅ Starts frontend server immediately

**Use when:**
- Already configured and just want to start servers
- Restarting during development
- No dependency or setup changes needed

---

## How the Scripts Work

### Windows (.bat files)

- Uses `start` command to open new terminal windows
- Each server runs in its own Command Prompt window
- Window titles: "OmniNode Backend" and "OmniNode Frontend"
- Press Ctrl+C in each window to stop servers
- Windows stay open after stopping for log review

### Unix/Linux/macOS (.sh files)

- Runs both servers as background processes
- Captures process IDs (PIDs) for management
- Single terminal shows status of both servers
- Press Ctrl+C once to stop both servers gracefully
- Includes cleanup trap for proper shutdown

---

## Stopping the Servers

### Windows
- Click the X button on terminal windows, or
- Press Ctrl+C in each terminal window

### Linux/macOS
- Press Ctrl+C in the launcher terminal
- Script will automatically kill both processes

To manually stop (if needed):
```bash
# Find processes
ps aux | grep "python main.py"
ps aux | grep "npm run dev"

# Kill by PID
kill <PID>
```

---

## Troubleshooting

### Port Already in Use

**Problem:** Port 8000 or 3000 already in use

**Solution:**
```bash
# Windows - Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS - Find and kill process
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### Setup Script Fails

**Problem:** Database or environment issues

**Solution:**
```bash
# Reset and try again
rm omninode.db
rm .env
python scripts/setup.py
```

### Frontend Won't Start

**Problem:** npm dependencies missing or corrupted

**Solution:**
```bash
cd frontend
rm -rf node_modules .next
npm install
cd ..
./start-quick.sh  # or start-quick.bat
```

### Permission Denied (Linux/macOS)

**Problem:** Script not executable

**Solution:**
```bash
chmod +x start.sh start-quick.sh
```

---

## Advanced Usage

### Custom Ports

Edit the scripts to use different ports:

**Backend:**
```python
# In backend/main.py, change:
uvicorn.run("main:app", host="0.0.0.0", port=8001)  # Changed from 8000
```

**Frontend:**
```bash
# Next.js will auto-suggest port 3001 if 3000 is taken
# Or set PORT environment variable:
PORT=3001 npm run dev
```

### Running Only Backend

```bash
cd backend
python main.py
```

### Running Only Frontend

```bash
cd frontend
npm run dev
```

### Development Mode with Auto-Reload

**Backend:**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:** (already has hot-reload)
```bash
cd frontend
npm run dev
```

---

## What Ports Are Used?

| Service | Port | URL |
|---------|------|-----|
| Backend API | 8000 | http://localhost:8000 |
| API Docs (Swagger) | 8000 | http://localhost:8000/docs |
| API Docs (ReDoc) | 8000 | http://localhost:8000/redoc |
| Frontend | 3000 | http://localhost:3000 |

---

## Environment Variables

The scripts use environment variables from `.env` file:

```bash
# Backend
DATABASE_URL=sqlite:///./omninode.db
SECRET_KEY=<generated-by-setup-script>
ENCRYPTION_KEY=<generated-by-setup-script>

# Frontend (optional)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## CI/CD Integration

For automated deployments:

```bash
# Run setup and start in production mode
python scripts/setup.py
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 &
cd frontend && npm run build && npm start &
```

---

## Next Steps After Launch

1. ✅ Verify backend: http://localhost:8000/health
2. ✅ Check API docs: http://localhost:8000/docs  
3. ✅ Open frontend: http://localhost:3000
4. ✅ Register your first MCP server (see [EXAMPLES.md](EXAMPLES.md))
5. ✅ Start using slash commands!

---

**Need help?** Check [SETUP.md](SETUP.md) for detailed setup instructions.
