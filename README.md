# CheckIn System

A comprehensive check-in/check-out system for tracking work hours, mood, and goals with team management capabilities.

## Features

- ✅ User authentication (register, login, token refresh)
- ✅ Check-in/Check-out functionality with location tracking
- ✅ Mood tracking (1-5 scale with emotions)
- ✅ Goal management and tracking
- ✅ Team management and collaboration
- ✅ Daily statistics and history
- ✅ JWT-based authentication
- ✅ Responsive UI with Tailwind CSS

## Tech Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT (python-jose)
- **Server**: Uvicorn

### Frontend
- **Framework**: Vue.js 3
- **Build Tool**: Vite
- **State Management**: Pinia
- **HTTP Client**: Axios
- **Styling**: Tailwind CSS
- **Language**: TypeScript

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 12+ (or Docker)
- Docker & Docker Compose (optional)

## Setup & Installation

### 1. Database Setup

Using Docker Compose (recommended):
```bash
cd checkin-system
docker-compose up -d
```

Or manually install PostgreSQL and create a database:
```sql
CREATE DATABASE checkin_db;
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (already created)
# Edit .env if needed for your configuration

# Run database migrations (optional - tables are created automatically)
# alembic upgrade head

# Start the development server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file (already created)
# The default API URL is http://localhost:8000

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Project Structure

```
checkin-system/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/        # API route handlers
│   │   ├── crud/                    # Database operations
│   │   ├── core/                    # Security, config
│   │   ├── db/                      # Database setup
│   │   ├── models/                  # SQLAlchemy models
│   │   ├── schemas/                 # Pydantic schemas
│   │   └── main.py                  # FastAPI app entry
│   ├── requirements.txt
│   ├── .env                         # Environment variables
│   └── .env.example                 # Example configuration
├── frontend/
│   ├── src/
│   │   ├── components/              # Vue components
│   │   ├── composables/             # Vue composition functions
│   │   ├── router/                  # Vue Router config
│   │   ├── services/                # API services
│   │   ├── stores/                  # Pinia stores
│   │   ├── types/                   # TypeScript types
│   │   ├── views/                   # Page components
│   │   ├── App.vue                  # Root component
│   │   └── main.ts                  # Entry point
│   ├── package.json
│   ├── .env                         # Environment variables
│   └── vite.config.ts               # Vite configuration
├── docker-compose.yml               # Docker database setup
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh access token

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update current user
- `GET /api/v1/users/{user_id}` - Get user profile

### Check-ins
- `POST /api/v1/checkins/check-in` - Record check-in
- `POST /api/v1/checkins/check-out` - Record check-out
- `GET /api/v1/checkins/today` - Get today's statistics
- `GET /api/v1/checkins` - Get checkin history
- `GET /api/v1/checkins/{checkin_id}` - Get specific checkin
- `PATCH /api/v1/checkins/{checkin_id}` - Update checkin
- `DELETE /api/v1/checkins/{checkin_id}` - Delete checkin

### Goals
- `POST /api/v1/goals` - Create goal
- `GET /api/v1/goals` - List goals
- `GET /api/v1/goals/{goal_id}` - Get goal
- `PATCH /api/v1/goals/{goal_id}` - Update goal
- `DELETE /api/v1/goals/{goal_id}` - Delete goal

### Teams
- `POST /api/v1/teams` - Create team
- `GET /api/v1/teams` - List user's teams
- `GET /api/v1/teams/{team_id}` - Get team details
- `POST /api/v1/teams/join` - Join team with code
- `POST /api/v1/teams/{team_id}/members/{user_id}/remove` - Remove member

## Frontend Routes

- `/login` - Login page
- `/register` - Registration page
- `/dashboard` - Main dashboard (requires auth)

## Usage

### Register & Login

1. Go to http://localhost:5173/register
2. Create a new account with email and password
3. Log in with your credentials

### Check In/Out

1. Navigate to the dashboard
2. Click "Check In" or "Check Out" button
3. Fill in details:
   - Mood level (1-5 scale)
   - Location name
   - Notes
4. Confirm the action

### Manage Goals

1. On the dashboard, you'll see today's goals
2. Create new goals by updating the goal state
3. Check off completed goals

### Team Management

1. Create a team or join existing team with code
2. Share team code with others to invite them
3. View team members and statistics

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/checkin_db
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## Development

### Run Tests (Backend)

```bash
cd backend
pytest
```

### Linting (Frontend)

```bash
cd frontend
npm run lint
npm run type-check
```

### Build for Production

Backend:
```bash
cd backend
pip install -r requirements.txt
# Use production ASGI server like Gunicorn
gunicorn app.main:app
```

Frontend:
```bash
cd frontend
npm run build
# Output in dist/ directory
```

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify credentials in docker-compose.yml

### CORS Errors
- Check CORS_ORIGINS in backend config
- Ensure frontend URL is in the allowed origins list

### Frontend API Errors
- Verify VITE_API_URL points to correct backend URL
- Check browser console for detailed error messages
- Ensure backend server is running on the specified port

## Future Enhancements

- [ ] Email notifications
- [ ] Advanced analytics and reporting
- [ ] Mobile app
- [ ] Real-time notifications
- [ ] Calendar integration
- [ ] Export functionality
- [ ] Multi-language support
- [ ] Dark mode

## License

MIT License

## Support

For issues and questions, please open an issue in the repository.
