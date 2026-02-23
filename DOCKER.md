# Docker Deployment Guide

## Quick Start - Deploy with Docker

This guide covers deploying the CheckIn System using Docker and Docker Compose.

---

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Domain name (for production)
- SSL certificate (optional but recommended)

---

## Development Deployment (Quick)

### 1. Start all services with Docker

```bash
cd checkin-system

# Start PostgreSQL only
docker-compose up -d

# Then run backend and frontend locally (as in SETUP.md)
```

---

## Production Deployment (Full Docker)

### 1. Prepare Environment

Create `.env` file in project root:

```env
# Database
DB_PASSWORD=your-secure-database-password
POSTGRES_USER=postgres
POSTGRES_DB=checkin_db

# JWT & Security
SECRET_KEY=your-very-long-secret-key-here

# Domain
DOMAIN=yourdomain.com

# Optional
APP_ENV=production
```

### 2. Build and Deploy

**Option A: Using docker-compose.prod.yml**

```bash
cd checkin-system

# Build images
docker-compose -f docker-compose.prod.yml build

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

**Option B: Build images manually**

```bash
# Build backend
docker build -t checkin-backend ./backend

# Build frontend
docker build -t checkin-frontend -f ./frontend/Dockerfile.prod ./frontend

# Run all services manually
docker run -d \
  --name checkin_postgres \
  -e POSTGRES_PASSWORD=password \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:16-alpine

docker run -d \
  --name checkin_backend \
  --link checkin_postgres:postgres \
  -e DATABASE_URL=postgresql://postgres:password@postgres:5432/checkin_db \
  -p 8000:8000 \
  checkin-backend

docker run -d \
  --name checkin_frontend \
  --link checkin_backend:backend \
  -p 80:80 \
  -p 443:443 \
  checkin-frontend
```

---

## SSL/TLS Setup

### Option 1: Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates to project
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./certs/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./certs/key.pem

# Update frontend/nginx.conf to uncomment SSL section

# Restart containers
docker-compose -f docker-compose.prod.yml restart frontend
```

### Option 2: Self-signed Certificate (Testing)

```bash
# Generate self-signed certificate
mkdir -p ./certs
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout ./certs/key.pem \
  -out ./certs/cert.pem \
  -days 365 \
  -subj "/CN=yourdomain.com"

# Update frontend/nginx.conf SSL section
# Restart containers
docker-compose -f docker-compose.prod.yml restart frontend
```

---

## Container Management

### View logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs

# Specific service
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend
docker-compose -f docker-compose.prod.yml logs postgres

# Follow logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Access containers

```bash
# Backend shell
docker-compose -f docker-compose.prod.yml exec backend bash

# Database shell
docker-compose -f docker-compose.prod.yml exec postgres psql -U postgres

# Frontend shell
docker-compose -f docker-compose.prod.yml exec frontend sh
```

### Stop services

```bash
# Stop all
docker-compose -f docker-compose.prod.yml down

# Stop all and remove volumes
docker-compose -f docker-compose.prod.yml down -v
```

### Restart services

```bash
# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend

# Restart all
docker-compose -f docker-compose.prod.yml restart
```

---

## Database Backup & Restore

### Backup

```bash
# Using docker-compose
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U postgres checkin_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backup (cron)
0 2 * * * docker-compose -f /path/to/docker-compose.prod.yml exec -T postgres \
  pg_dump -U postgres checkin_db > /backups/checkin_db_$(date +\%Y\%m\%d).sql
```

### Restore

```bash
docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U postgres -d checkin_db < backup_20240101_120000.sql
```

---

## Scaling & Performance

### Increase backend workers

Edit `docker-compose.prod.yml`:

```yaml
backend:
  environment:
    - GUNICORN_CMD_ARGS=--workers 8 --worker-class uvicorn.workers.UvicornWorker
```

### Database connection pooling

Already configured in backend - adjust in `backend/app/db/session.py`:

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=30,        # Increase if needed
    max_overflow=60,
    pool_pre_ping=True
)
```

### Frontend caching

Nginx configuration includes:
- Static asset caching (1 year)
- Gzip compression
- Health checks

---

## Monitoring

### Health checks

```bash
# Frontend health
curl http://localhost/health

# Backend health (if exposed)
curl http://localhost:8000/health

# Database health
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_isready -U postgres
```

### Resource usage

```bash
# Container stats
docker stats

# Specific container
docker stats checkin_backend
```

---

## Security Best Practices

### 1. Environment Variables

- Store `.env` in secure location
- Use strong passwords for database
- Rotate SECRET_KEY regularly

### 2. File Permissions

```bash
chmod 600 .env
chmod 600 ./certs/*
```

### 3. Network Isolation

Both `docker-compose` configurations use isolated networks:
- `checkin_network` for internal communication
- No external access except through Nginx

### 4. Container Security

- Run containers as non-root (handled by images)
- Use read-only volumes where possible
- Regularly update base images

```bash
# Update images
docker pull postgres:16-alpine
docker pull node:18-alpine
docker pull nginx:alpine
```

---

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Inspect container
docker inspect checkin_backend

# Check health
docker ps --filter "name=checkin_backend"
```

### Database connection errors

```bash
# Check connectivity from backend
docker-compose -f docker-compose.prod.yml exec backend \
  python -c "import psycopg2; psycopg2.connect('dbname=checkin_db user=postgres password=password host=postgres')"

# Restart database
docker-compose -f docker-compose.prod.yml restart postgres
```

### Frontend not showing API data

```bash
# Check Nginx proxy configuration
docker-compose -f docker-compose.prod.yml exec frontend \
  cat /etc/nginx/nginx.conf | grep -A 10 "location /api"

# Check backend is running
docker-compose -f docker-compose.prod.yml exec backend \
  curl http://localhost:8000/health
```

### Disk space issues

```bash
# Remove unused images and containers
docker system prune

# Remove unused volumes
docker volume prune

# Check disk usage
docker system df
```

---

## Updates & Maintenance

### Update application

```bash
# Pull latest code
git pull

# Rebuild images
docker-compose -f docker-compose.prod.yml build --no-cache

# Restart services
docker-compose -f docker-compose.prod.yml up -d
```

### Update dependencies

```bash
# Backend
cd backend
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm update

# Rebuild Docker images
docker-compose -f docker-compose.prod.yml build --no-cache
```

---

## Production Checklist

- [ ] Environment variables configured
- [ ] SSL certificates obtained
- [ ] Database backups automated
- [ ] Logs are being collected
- [ ] Health checks configured
- [ ] Resource limits set
- [ ] Security policies reviewed
- [ ] Monitoring/alerts set up
- [ ] Rollback plan documented

---

## Docker Compose Reference

### Services in docker-compose.prod.yml

| Service | Port | Container | Description |
|---------|------|-----------|-------------|
| postgres | 5432 | checkin_postgres | PostgreSQL database |
| backend | 8000 | checkin_backend | FastAPI application |
| frontend | 80,443 | checkin_frontend | Vue + Nginx |

### Important files

| Path | Purpose |
|------|---------|
| `docker-compose.prod.yml` | Production compose file |
| `backend/Dockerfile` | Backend image definition |
| `frontend/Dockerfile.prod` | Frontend image definition |
| `frontend/nginx.conf` | Nginx configuration |
| `.env` | Environment variables |
| `certs/` | SSL certificates |

---

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL in Docker](https://hub.docker.com/_/postgres)

---

**Good luck with your deployment!** 🚀

