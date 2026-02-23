# API Documentation

## Base URL
- Development: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs

## Authentication

### Token-Based Authentication
All protected endpoints require an `Authorization` header with a Bearer token:

```
Authorization: Bearer <access_token>
```

### Token Expiry
- Access tokens expire in 30 minutes
- Refresh tokens expire in 7 days
- Implement automatic token refresh using the `/api/v1/auth/refresh` endpoint

## Response Format

### Success Response
```json
{
  "id": "uuid",
  "field": "value",
  ...
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

## Endpoints

### Authentication

#### Register User
```
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}

Response: 201 Created
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "avatar_url": null,
  "timezone": "UTC",
  "is_active": true,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

#### Login
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Refresh Token
```
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Users

#### Get Current User
```
GET /api/v1/users/me
Authorization: Bearer <token>

Response: 200 OK
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "avatar_url": null,
  "timezone": "UTC",
  "is_active": true,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

#### Update User Profile
```
PUT /api/v1/users/me
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "Jane Doe",
  "avatar_url": "https://...",
  "timezone": "Asia/Bangkok"
}

Response: 200 OK
{...updated user}
```

### Check-ins

#### Check In
```
POST /api/v1/checkins/check-in
Authorization: Bearer <token>
Content-Type: application/json

{
  "location_latitude": 13.7563,
  "location_longitude": 100.5018,
  "location_name": "Office",
  "notes": "Starting work",
  "mood": {
    "mood_level": 4,
    "emotion": "focused",
    "notes": "Feeling productive"
  },
  "goal_id": "uuid (optional)"
}

Response: 201 Created
{
  "id": "uuid",
  "user_id": "uuid",
  "status": "checked_in",
  "timestamp": "2024-01-01T09:00:00",
  "location_latitude": 13.7563,
  "location_longitude": 100.5018,
  "location_name": "Office",
  "notes": "Starting work",
  "duration_minutes": null,
  "mood": {...},
  "goal_id": null,
  "created_at": "2024-01-01T09:00:00",
  "updated_at": "2024-01-01T09:00:00"
}
```

#### Check Out
```
POST /api/v1/checkins/check-out
Authorization: Bearer <token>
Content-Type: application/json

{
  "notes": "Great day!",
  "mood": {
    "mood_level": 5,
    "emotion": "happy",
    "notes": "Accomplished a lot"
  }
}

Response: 201 Created
{
  "id": "uuid",
  "user_id": "uuid",
  "status": "checked_out",
  "timestamp": "2024-01-01T17:00:00",
  "location_latitude": null,
  "location_longitude": null,
  "location_name": null,
  "notes": "Great day!",
  "duration_minutes": 480,
  "mood": {...},
  "goal_id": null,
  "created_at": "2024-01-01T17:00:00",
  "updated_at": "2024-01-01T17:00:00"
}
```

#### Get Today's Statistics
```
GET /api/v1/checkins/today
Authorization: Bearer <token>

Response: 200 OK
{
  "total_checkins_today": 2,
  "is_checked_in": false,
  "latest_checkin": {...},
  "total_duration_minutes": 480,
  "mood_history": [...]
}
```

#### Get Checkins (History)
```
GET /api/v1/checkins?skip=0&limit=50
Authorization: Bearer <token>

Response: 200 OK
[{...checkin}, ...]
```

#### Get Specific Checkin
```
GET /api/v1/checkins/{checkin_id}
Authorization: Bearer <token>

Response: 200 OK
{...checkin}
```

#### Update Checkin
```
PATCH /api/v1/checkins/{checkin_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "notes": "Updated notes",
  "location_name": "New Location"
}

Response: 200 OK
{...updated checkin}
```

#### Delete Checkin
```
DELETE /api/v1/checkins/{checkin_id}
Authorization: Bearer <token>

Response: 204 No Content
```

### Goals

#### Create Goal
```
POST /api/v1/goals
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Complete project report",
  "description": "Finish Q1 analysis",
  "priority": "high"
}

Response: 201 Created
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "Complete project report",
  "description": "Finish Q1 analysis",
  "is_completed": false,
  "priority": "high",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

#### Get Goals
```
GET /api/v1/goals?completed=false&skip=0&limit=50
Authorization: Bearer <token>

Query Parameters:
- completed (optional): true/false to filter by completion status
- skip: Pagination offset (default: 0)
- limit: Number of results (default: 50, max: 100)

Response: 200 OK
[{...goal}, ...]
```

#### Update Goal
```
PATCH /api/v1/goals/{goal_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated title",
  "is_completed": true,
  "priority": "medium"
}

Response: 200 OK
{...updated goal}
```

#### Delete Goal
```
DELETE /api/v1/goals/{goal_id}
Authorization: Bearer <token>

Response: 204 No Content
```

### Teams

#### Create Team
```
POST /api/v1/teams
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Development Team",
  "description": "Backend developers"
}

Response: 201 Created
{
  "id": "uuid",
  "name": "Development Team",
  "code": "ABC123",
  "description": "Backend developers",
  "created_by": "uuid",
  "is_active": true,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

#### Get User's Teams
```
GET /api/v1/teams
Authorization: Bearer <token>

Response: 200 OK
[{...team}, ...]
```

#### Get Team Details
```
GET /api/v1/teams/{team_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "id": "uuid",
  "name": "Development Team",
  "code": "ABC123",
  "description": "Backend developers",
  "created_by": "uuid",
  "is_active": true,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00",
  "members": [
    {
      "user_id": "uuid",
      "role": "owner",
      "joined_at": "2024-01-01T12:00:00"
    }
  ]
}
```

#### Join Team
```
POST /api/v1/teams/join
Authorization: Bearer <token>
Content-Type: application/json

{
  "team_code": "ABC123"
}

Response: 200 OK
{...team}
```

#### Remove Team Member
```
POST /api/v1/teams/{team_id}/members/{user_id}/remove
Authorization: Bearer <token>

Response: 204 No Content
```

## Error Codes

### Common Status Codes
- `200 OK` - Successful GET/PUT/PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - User doesn't have permission
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Rate Limiting

Currently no rate limiting is implemented. This should be added for production.

## Running Tests

```bash
cd backend
pytest
```

## API Versioning

The API is versioned at v1. Future versions will use:
- `/api/v2/...`
- `/api/v3/...`
- etc.

