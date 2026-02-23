@echo off
setlocal enabledelayedexpansion

echo ================================
echo CheckIn System - Development Setup
echo ================================

REM Check if Docker is available
where docker >nul 2>nul
if !errorlevel! equ 0 (
    echo.
    echo Starting PostgreSQL database with Docker...
    docker-compose up -d
    timeout /t 3 /nobreak
    echo OK - Database started
) else (
    echo.
    echo WARNING - Docker not found. Please start PostgreSQL manually and ensure:
    echo    - Database is running on localhost:5432
    echo    - Database user: postgres, password: postgres
    echo    - Database name: checkin_db
)

echo.
echo ================================
echo Starting Backend Server
echo ================================

cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo OK - Starting FastAPI server on http://localhost:8000
start cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo ================================
echo Starting Frontend Server
echo ================================

cd ..\frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

echo OK - Starting Vue.js dev server on http://localhost:5173
start cmd /k "npm run dev"

echo.
echo ================================
echo OK - All services started!
echo ================================
echo.
echo Services:
echo   - Frontend:  http://localhost:5173
echo   - Backend:   http://localhost:8000
echo   - API Docs:  http://localhost:8000/docs
echo.
echo New terminal windows have been opened for each service.
echo Close them to stop the servers.
echo.
pause
