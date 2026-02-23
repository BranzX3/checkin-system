#!/bin/bash

echo "================================"
echo "CheckIn System - Development Setup"
echo "================================"

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo ""
    echo "Starting PostgreSQL database with Docker..."
    docker-compose up -d
    sleep 3
    echo "✓ Database started"
else
    echo ""
    echo "⚠️  Docker not found. Please start PostgreSQL manually and ensure:"
    echo "   - Database is running on localhost:5432"
    echo "   - Database user: postgres, password: postgres"
    echo "   - Database name: checkin_db"
fi

echo ""
echo "================================"
echo "Starting Backend Server"
echo "================================"

cd backend || exit 1

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "✓ Starting FastAPI server on http://localhost:8000"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo ""
echo "================================"
echo "Starting Frontend Server"
echo "================================"

cd ../frontend || exit 1

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo "✓ Starting Vue.js dev server on http://localhost:5173"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "================================"
echo "✅ All services started!"
echo "================================"
echo ""
echo "Services:"
echo "  - Frontend:  http://localhost:5173"
echo "  - Backend:   http://localhost:8000"
echo "  - API Docs:  http://localhost:8000/docs"
echo ""
echo "To stop the servers, press Ctrl+C"
echo ""

wait
