@echo off
REM OmniNode Launcher for Windows
REM This script sets up and launches the OmniNode application

echo ========================================
echo    OmniNode Launcher
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.12+ and try again
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js 20+ and try again
    pause
    exit /b 1
)

echo [1/5] Installing Python dependencies...
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)
echo Installing backend packages...
pip install -e ".[dev]" --quiet
if errorlevel 1 (
    echo [ERROR] Python dependency installation failed
    pause
    exit /b 1
)
echo.

echo [2/5] Running setup script...
python scripts\setup.py
if errorlevel 1 (
    echo [ERROR] Setup failed
    pause
    exit /b 1
)
echo.

echo [3/5] Installing frontend dependencies...
cd frontend
if not exist "node_modules" (
    echo Installing npm packages for the first time...
    call npm install
    if errorlevel 1 (
        echo [ERROR] npm install failed
        cd ..
        pause
        exit /b 1
    )
) else (
    echo npm packages already installed, skipping...
)
cd ..
echo.

echo [4/5] Starting backend server...
echo Opening new terminal for backend...
start "OmniNode Backend" cmd /k "cd /d %~dp0backend && python main.py"
timeout /t 3 /nobreak >nul
echo.

echo [5/5] Starting frontend server...
echo Opening new terminal for frontend...
start "OmniNode Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
echo.

echo ========================================
echo    OmniNode is starting!
echo ========================================
echo.
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:3000
echo API Documentation: http://localhost:8000/docs
echo.
echo Check the opened terminal windows for logs.
echo Press Ctrl+C in each terminal to stop the servers.
echo.
pause
