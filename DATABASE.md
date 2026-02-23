# Database Schema

## Overview

The CheckIn System uses PostgreSQL as its primary database. The schema includes tables for users, teams, check-ins, moods, and goals.

## Tables

### Users Table
Stores user account information.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    avatar_url VARCHAR(500),
    timezone VARCHAR(50) DEFAULT 'UTC',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

**Fields:**
- `id`: Unique identifier (UUID)
- `email`: User's email address (unique)
- `hashed_password`: Bcrypt hashed password
- `full_name`: User's full name
- `avatar_url`: URL to user's avatar
- `timezone`: User's timezone
- `is_active`: Whether account is active
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

---

### Teams Table
Stores team information created by users.

```sql
CREATE TABLE teams (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    description VARCHAR(500),
    created_by UUID NOT NULL REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_teams_code ON teams(code);
```

**Fields:**
- `id`: Unique identifier
- `name`: Team name
- `code`: Unique 6-character code for joining
- `description`: Team description
- `created_by`: User ID of team creator
- `is_active`: Whether team is active
- `created_at`: Team creation timestamp
- `updated_at`: Last update timestamp

---

### TeamMembers Table
Maps users to teams with their roles.

```sql
CREATE TABLE team_members (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_team UNIQUE(user_id, team_id)
);

CREATE INDEX idx_team_members_user ON team_members(user_id);
CREATE INDEX idx_team_members_team ON team_members(team_id);
```

**Fields:**
- `id`: Unique identifier
- `user_id`: User ID
- `team_id`: Team ID
- `role`: User's role ('owner', 'manager', 'member')
- `joined_at`: When user joined the team

**Role Hierarchy:**
- `owner`: Can manage team and members
- `manager`: Can view team analytics
- `member`: Can participate in team

---

### Checkins Table
Records user check-in and check-out events.

```sql
CREATE TABLE checkins (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    location_latitude FLOAT,
    location_longitude FLOAT,
    location_name VARCHAR(255),
    notes VARCHAR(1000),
    duration_minutes INTEGER,
    mood_id UUID REFERENCES moods(id) ON DELETE SET NULL,
    goal_id UUID REFERENCES goals(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_checkins_user ON checkins(user_id);
CREATE INDEX idx_checkins_timestamp ON checkins(timestamp);
```

**Fields:**
- `id`: Unique identifier
- `user_id`: User ID
- `status`: 'checked_in' or 'checked_out'
- `timestamp`: When check-in occurred
- `location_latitude`: GPS latitude
- `location_longitude`: GPS longitude
- `location_name`: Name of location (e.g., 'Office')
- `notes`: User notes
- `duration_minutes`: Time spent (for check-outs)
- `mood_id`: Associated mood record
- `goal_id`: Associated goal
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp

---

### Moods Table
Tracks user mood at specific times.

```sql
CREATE TABLE moods (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    checkin_id UUID REFERENCES checkins(id) ON DELETE SET NULL,
    mood_level INTEGER NOT NULL,
    emotion VARCHAR(50),
    notes VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_moods_user ON moods(user_id);
```

**Fields:**
- `id`: Unique identifier
- `user_id`: User ID
- `checkin_id`: Associated check-in
- `mood_level`: 1-5 scale
- `emotion`: Emotion description (e.g., 'happy', 'stressed')
- `notes`: Additional notes
- `created_at`: Record creation timestamp

**Mood Levels:**
- 1: Very sad/worst
- 2: Sad/bad
- 3: Neutral/okay
- 4: Happy/good
- 5: Very happy/best

---

### Goals Table
Stores user goals and their completion status.

```sql
CREATE TABLE goals (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(1000),
    is_completed BOOLEAN DEFAULT FALSE,
    priority VARCHAR(20) DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_goals_user ON goals(user_id);
```

**Fields:**
- `id`: Unique identifier
- `user_id`: User ID
- `title`: Goal title
- `description`: Goal description
- `is_completed`: Whether goal is completed
- `priority`: 'high', 'medium', 'low'
- `created_at`: Goal creation timestamp
- `updated_at`: Last update timestamp

---

## Relationships

```
User (1) ──→ (Many) Checkins
User (1) ──→ (Many) Moods
User (1) ──→ (Many) Goals
User (1) ──→ (Many) Teams (created_by)

Team (1) ──→ (Many) TeamMembers
User (1) ──→ (Many) TeamMembers

Checkin (1) ──→ (0-1) Mood
Checkin (1) ──→ (0-1) Goal
Goal (1) ──→ (Many) Checkins
Mood (1) ──→ (0-1) Checkin
```

## Indexes

Created for performance optimization:

- `idx_users_email`: Fast email lookups
- `idx_teams_code`: Fast team code lookups
- `idx_team_members_user`: Find all teams for a user
- `idx_team_members_team`: Find all members in a team
- `idx_checkins_user`: Find user's check-ins
- `idx_checkins_timestamp`: Find check-ins by date/time
- `idx_moods_user`: Find user's moods
- `idx_goals_user`: Find user's goals

## Cascading Deletes

- Deleting a user cascades to:
  - All checkins
  - All moods
  - All goals
  - All team memberships
  - But not teams created by them (for data integrity)

- Deleting a team cascades to:
  - All team memberships

## Data Retention

### Recommended Policies

- **Checkins**: Keep indefinitely (useful for analytics)
- **Moods**: Keep for 2 years
- **Goals**: Keep indefinitely
- **Teams**: Delete inactive teams after 1 year
- **User Accounts**: Archive after 1 year of inactivity

## Backup Strategy

```bash
# Daily backup
pg_dump -h localhost -U postgres -d checkin_db > backup_$(date +%Y%m%d).sql

# Weekly backup with compression
pg_dump -h localhost -U postgres -d checkin_db | gzip > backup_$(date +%Y%m%d).sql.gz

# Full system backup
pg_basebackup -h localhost -U postgres -D /backups/pg_backup -Ft -z -P
```

## Performance Considerations

1. **Checkins Table**: Can grow large quickly
   - Consider partitioning by month/quarter for very large datasets
   - Archive old data to separate storage

2. **Queries**: Use indexes effectively
   - Always filter by user_id for multi-tenant queries
   - Use date ranges for historical queries

3. **Connections**: Current pool size is 10, adjustable in session.py

4. **VACUUM**: Run regularly on large tables
   ```sql
   VACUUM ANALYZE users;
   VACUUM ANALYZE checkins;
   ```

## Migration

Use Alembic for database migrations:

```bash
# Create migration
alembic revision --autogenerate -m "Add new column"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Monitoring

Monitor database performance:

```sql
-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables 
WHERE schemaname != 'pg_catalog'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check slow queries
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;

-- Check active connections
SELECT usename, datname, count(*) 
FROM pg_stat_activity 
GROUP BY usename, datname;
```

