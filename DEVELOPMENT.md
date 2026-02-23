# Development Guide

## For Developers

This guide explains the architecture and how to extend the CheckIn System.

---

## Project Architecture

### Backend Architecture

```
┌─────────────────────────────────────────┐
│         FastAPI Application              │
├─────────────────────────────────────────┤
│  Route Handlers (api/v1/endpoints/*.py) │
│  ├── auth.py       (Authentication)    │
│  ├── users.py      (User management)   │
│  ├── checkins.py   (Check-in ops)      │
│  ├── goals.py      (Goal management)   │
│  └── teams.py      (Team management)   │
├─────────────────────────────────────────┤
│  CRUD Layer (crud/*.py)                  │
│  ├── user.py       (User CRUD)          │
│  ├── checkin.py    (Checkin CRUD)       │
│  ├── goal.py       (Goal CRUD)          │
│  ├── team.py       (Team CRUD)          │
│  └── mood.py       (Mood CRUD)          │
├─────────────────────────────────────────┤
│  Database Layer                          │
│  ├── models/*.py   (SQLAlchemy Models)  │
│  ├── schemas/*.py  (Pydantic Schemas)   │
│  └── session.py    (DB Connection)      │
├─────────────────────────────────────────┤
│  Core Services                           │
│  ├── security.py   (JWT, Passwords)     │
│  └── config.py     (Configuration)      │
├─────────────────────────────────────────┤
│         PostgreSQL Database              │
└─────────────────────────────────────────┘
```

### Frontend Architecture

```
┌────────────────────────────────────┐
│      Vue 3 Application (main.ts)   │
├────────────────────────────────────┤
│      App.vue (Root Component)       │
├────────────────────────────────────┤
│  Router (router/index.ts)           │
│  ├── /login       (LoginForm)       │
│  ├── /register    (RegisterForm)    │
│  └── /dashboard   (DashboardView)   │
├────────────────────────────────────┤
│  Views (views/*.vue)                │
│  ├── AuthView.vue                   │
│  └── DashboardView.vue              │
├────────────────────────────────────┤
│  Components (components/*.vue)      │
│  ├── LoginForm.vue                  │
│  ├── RegisterForm.vue               │
│  ├── StatusCard.vue                 │
│  └── HistoryList.vue                │
├────────────────────────────────────┤
│  State Management (stores/*.ts)     │
│  ├── auth.ts       (Auth Store)     │
│  ├── checkin.ts    (Checkin Store)  │
│  └── team.ts       (Team Store)     │
├────────────────────────────────────┤
│  Services (services/*.ts)           │
│  ├── api.ts        (Axios instance) │
│  ├── authService.ts                 │
│  ├── checkinService.ts              │
│  └── teamService.ts                 │
├────────────────────────────────────┤
│  Composables (composables/*.ts)     │
│  ├── useAuth.ts                     │
│  ├── useCheckin.ts                  │
│  └── useLocation.ts                 │
├────────────────────────────────────┤
└────────────────────────────────────┘
```

---

## Adding New Features

### Backend: Adding a New Endpoint

**Example: Add endpoint to get user analytics**

1. **Create the CRUD operation** (`app/crud/analytics.py`):
```python
from sqlalchemy.orm import Session
from app.models import Checkin
from datetime import datetime, timedelta
from uuid import UUID

class CRUDAnalytics:
    def get_weekly_stats(self, db: Session, user_id: UUID):
        """Get analytics for the past week."""
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)
        
        checkins = db.query(Checkin).filter(
            Checkin.user_id == user_id,
            Checkin.timestamp >= datetime.combine(week_ago, datetime.min.time())
        ).all()
        
        return {
            "total_checkins": len(checkins),
            "avg_duration": sum(c.duration_minutes or 0 for c in checkins) / len(checkins if checkins else [1]),
            "checkins": checkins
        }

crud_analytics = CRUDAnalytics()
```

2. **Create the schema** (`app/schemas/analytics.py`):
```python
from pydantic import BaseModel
from typing import Optional, List

class WeeklyStatsResponse(BaseModel):
    total_checkins: int
    avg_duration: float
    checkins: List[dict]
```

3. **Create the endpoint** (`app/api/v1/endpoints/analytics.py`):
```python
from fastapi import APIRouter, Depends
from app.crud.analytics import crud_analytics
from app.db.session import get_db
from app.api.v1.endpoints.checkins import get_current_user
from app.schemas.analytics import WeeklyStatsResponse

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

@router.get("/weekly", response_model=WeeklyStatsResponse)
def get_weekly_stats(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get weekly analytics."""
    return crud_analytics.get_weekly_stats(db, current_user.id)
```

4. **Include the router** in `app/main.py`:
```python
from app.api.v1.endpoints import analytics
app.include_router(analytics.router)
```

### Frontend: Adding a New Component

**Example: Add analytics widget to dashboard**

1. **Create the component** (`src/components/AnalyticsWidget.vue`):
```vue
<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h2 class="text-xl font-bold mb-4">Weekly Stats</h2>
    
    <div v-if="loading" class="text-gray-500">Loading...</div>
    <div v-else-if="stats" class="space-y-3">
      <div class="flex justify-between">
        <span>Total Check-ins:</span>
        <span class="font-semibold">{{ stats.total_checkins }}</span>
      </div>
      <div class="flex justify-between">
        <span>Avg Duration:</span>
        <span class="font-semibold">{{ Math.round(stats.avg_duration) }} min</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const loading = ref(false)
const stats = ref(null)

onMounted(async () => {
  loading.value = true
  try {
    const response = await api.get('/api/v1/analytics/weekly')
    stats.value = response.data
  } finally {
    loading.value = false
  }
})
</script>
```

2. **Add to dashboard** (`src/views/DashboardView.vue`):
```vue
<template>
  <div class="space-y-8">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <StatusCard />
      <AnalyticsWidget />
      <!-- ... other components ... -->
    </div>
  </div>
</template>

<script setup lang="ts">
import AnalyticsWidget from '@/components/AnalyticsWidget.vue'
// ...
</script>
```

---

## Modifying Database Schema

### Add a New Column

1. **Update the model** (`app/models/__init__.py`):
```python
class Checkin(Base):
    __tablename__ = "checkins"
    
    # ... existing columns ...
    weather = Column(String(50), nullable=True)  # New column
```

2. **Create database migration** (if using Alembic):
```bash
alembic revision --autogenerate -m "Add weather column to checkins"
alembic upgrade head
```

3. **Update the schema** (`app/schemas/checkin.py`):
```python
class CheckinResponse(BaseModel):
    # ... existing fields ...
    weather: Optional[str] = None
```

### Add a New Table

1. **Create the model** in `app/models/__init__.py`
2. **Update imports** in main.py if needed
3. **Create CRUD operations** in `app/crud/`
4. **Create endpoints** in `app/api/v1/endpoints/`
5. **Run database migration**

---

## Environment-Specific Configuration

### Development
```env
DEBUG=True
SQLALCHEMY_ECHO=True
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

### Staging
```env
DEBUG=False
SQLALCHEMY_ECHO=False
CORS_ORIGINS=["https://staging.example.com"]
```

### Production
```env
DEBUG=False
SQLALCHEMY_ECHO=False
CORS_ORIGINS=["https://example.com"]
DATABASE_URL=postgresql://prod_user:secure_password@prod_db:5432/checkin_db
SECRET_KEY=very-long-random-secure-key
```

---

## Testing

### Backend Testing

1. **Create test file** (`tests/test_endpoints.py`):
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
```

2. **Run tests**:
```bash
pytest
pytest -v  # Verbose
pytest --cov  # With coverage
```

### Frontend Testing

1. **Install testing library**:
```bash
npm install --save-dev vitest @vue/test-utils
```

2. **Create test file** (`src/components/__tests__/LoginForm.spec.ts`):
```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LoginForm from '@/components/LoginForm.vue'

describe('LoginForm', () => {
  it('renders login form', () => {
    const wrapper = mount(LoginForm)
    expect(wrapper.find('input[type="email"]').exists()).toBe(true)
  })
})
```

3. **Run tests**:
```bash
npm run test
```

---

## Debugging

### Backend Debugging

1. **Enable verbose logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **Use debugger** (VS Code):
Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "jinja": true
    }
  ]
}
```

### Frontend Debugging

1. **Vue DevTools**: Install browser extension
2. **Console**: Check browser console for errors
3. **Network**: Check Network tab for API calls
4. **VS Code**: Debug with Debugger for Chrome extension

---

## Code Style

### Backend

Follow PEP 8:
```bash
pip install black flake8

# Format code
black .

# Lint
flake8 .
```

### Frontend

Follow ESLint config:
```bash
npm run lint  # Check
npm run lint -- --fix  # Fix automatically
```

---

## Common Tasks

### Add Authentication to New Endpoint

```python
@router.get("/protected")
def protected_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # User is authenticated, current_user is available
    return {"user_id": current_user.id}
```

### Add Pagination

```python
@router.get("/items")
def get_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    items = db.query(Item).offset(skip).limit(limit).all()
    return items
```

### Add Request Validation

```python
from pydantic import Field, validator

class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    value: int = Field(..., ge=0, le=1000)
    
    @validator('name')
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v
```

### Handle Errors Gracefully

```python
@router.get("/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )
    return item
```

---

## Performance Tips

### Database
- Use `.select()` instead of loading all data
- Add indexes on frequently filtered columns
- Use connection pooling (already configured)
- Paginate large result sets

### API
- Use response caching where appropriate
- Compress responses (gzip)
- Batch operations when possible
- Use CDN for static assets

### Frontend
- Lazy load components
- Use v-show for toggled elements
- Implement virtual scrolling for large lists
- Minimize bundle size with tree-shaking

---

## Security Best Practices

### Backend
- Validate all inputs (using Pydantic)
- Use parameterized queries (ORM handles this)
- Never log sensitive data
- Rate limit public endpoints
- Use HTTPS in production

### Frontend
- Never store sensitive data in localStorage
- Sanitize user inputs
- Use Content Security Policy
- Keep dependencies updated

---

## Version Updates

### Update Dependencies

```bash
# Backend
pip list --outdated
pip install --upgrade package_name

# Frontend
npm outdated
npm update
```

### Test After Updates
```bash
# Backend
pytest

# Frontend
npm run build
npm run test
```

---

## Troubleshooting

### Still having issues?

1. Check the logs
2. Review error messages carefully
3. Search existing documentation
4. Check related tests for examples
5. Use debugger to step through code

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue 3 Documentation](https://vuejs.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

---

Happy coding! 🚀

