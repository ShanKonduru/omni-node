@echo off
REM Quick Start - OmniNode (Skip setup if already configured)

echo ========================================
echo    OmniNode Quick Start
echo ========================================
echo.

echo Starting backend server...
start "OmniNode Backend" cmd /k "cd /d %~dp0backend && python main.py"
timeout /t 2 /nobreak >nul

echo Starting frontend server...
start "OmniNode Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
