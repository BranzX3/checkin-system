# CheckIn System - Quick Start Guide

## Prerequisites

Before getting started, make sure you have the following installed:

- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Docker & Docker Compose** (optional but recommended) - [Download](https://www.docker.com/products/docker-desktop)
- **PostgreSQL 12+** (if not using Docker)

## Quick Start (5 Minutes)

### Option A: Using Docker (Recommended)

1. **Clone or navigate to the project:**
   ```bash
   cd checkin-system
   ```

2. **Run the startup script:**

   **On macOS/Linux:**
   ```bash
   chmod +x start-dev.sh
   ./start-dev.sh
   ```

   **On Windows:**
   ```bash
   start-dev.bat
   ```

3. **Open in browser:**
   - Frontend: http://localhost:5173
   - Backend API Docs: http://localhost:8000/docs

4. **Create an account and start using the app!**
 
### Option B: Manual Setup

#### Step 1: Start Database

**Using Docker:**
```bash
docker-compose up -d
```

**Or manually:**
- Install and start PostgreSQL
- Create database:
  ```sql
  CREATE DATABASE checkin_db;
  ```

#### Step 2: Start Backend Server

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server
python -m uvicorn app.main:app --reload
```

Backend will be available at: `http://localhost:8000`

#### Step 3: Start Frontend Server

In a new terminal:

```bash
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## First Time Setup

### 1. Register a New Account
- Go to http://localhost:5173/register
- Fill in your email and password
- Click "Register"

### 2. First Check-In
- Navigate to the dashboard
- Click the "Check In" button
- Select your mood, location, and add notes
- Click "Confirm"

### 3. Create a Team (Optional)
- In dashboard, create a team
- Share the team code with others
- Team members can join with the code

## Common Issues & Solutions

### PostgreSQL Connection Error
**Problem:** `psycopg2.OperationalError`

**Solution:**
1. Ensure PostgreSQL is running
2. Check credentials in `backend/.env`:
   - `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/checkin_db`
3. Verify database exists:
   ```sql
   CREATE DATABASE checkin_db;
   ```

### CORS Error in Console
**Problem:** `Access to XMLHttpRequest blocked by CORS policy`

**Solution:**
1. Ensure backend is running on port 8000
2. Check frontend `.env` has correct API URL:
   ```
   VITE_API_URL=http://localhost:8000
   ```

### Port Already in Use
**Problem:** `Address already in use`

**Solution:**
- Change the port in the startup command:
  - Frontend: `npm run dev -- --port 5174`
  - Backend: `python -m uvicorn app.main:app --port 8001`

### Python Virtual Environment Issues
**Problem:** Python packages not installing

**Solution:**
```bash
# Remove old venv
rm -rf venv  # or rmdir venv on Windows

# Create fresh venv
python -m venv venv

# Activate and reinstall
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Environment Files

### Backend Configuration (backend/.env)
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/checkin_db
SECRET_KEY=your-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DEBUG=False
```

### Frontend Configuration (frontend/.env)
```
VITE_API_URL=http://localhost:8000
```

## Available Commands

### Backend
```bash
cd backend

# Run development server
python -m uvicorn app.main:app --reload

# Run tests
pytest

# Format code
black .

# Lint
flake8 .
```

### Frontend
```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint and fix
npm run lint

# Type checking
npm run type-check
```

## Project Structure

```
checkin-system/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── crud/            # Database CRUD operations
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── main.py          # App entry point
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables
├── frontend/                # Vue 3 frontend
│   ├── src/
│   │   ├── components/      # Vue components
│   │   ├── stores/          # Pinia stores
│   │   ├── services/        # API services
│   │   └── main.ts          # App entry point
│   ├── package.json         # Node dependencies
│   └── .env                 # Environment variables
├── docker-compose.yml       # Docker database setup
└── README.md               # Full documentation
```

## Next Steps

1. **Explore the Dashboard**
   - Check in and out throughout the day
   - Track your mood and notes
   - Monitor your daily statistics

2. **Create Goals**
   - Set daily or weekly goals
   - Track goal completion
   - View goal history

3. **Collaborate with Teams**
   - Create or join teams
   - Share team codes
   - View team member activity

4. **Review Analytics**
   - Check daily/weekly statistics
   - View mood trends
   - Analyze work patterns

## Documentation

- **Full Documentation**: See [README.md](README.md)
- **API Documentation**: http://localhost:8000/docs (when backend is running)
- **Frontend Code**: See `frontend/src` directory

## Getting Help

If you encounter issues:
1. Check the [Common Issues](#common-issues--solutions) section
2. Check existing issues in the repository
3. Look at the logs in the terminal where services are running
4. Open a new issue with:
   - Error message
   - Steps to reproduce
   - Your environment (OS, Python/Node version, etc.)

## Stopping Services

### Using startup script:
- Press `Ctrl+C` in the terminal running the script

### Manual setup:
- Stop backend: Press `Ctrl+C` in backend terminal
- Stop frontend: Press `Ctrl+C` in frontend terminal
- Stop database: `docker-compose down` (if using Docker)

## Production Deployment

For production deployment, see the [Production Deployment Guide](DEPLOYMENT.md) (if available).

---

Happy tracking! 🎯

