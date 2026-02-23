# Deployment Guide

## Production Deployment

This guide covers deploying the CheckIn System to a production environment.

## Pre-Deployment Checklist

- [ ] Environment variables configured
- [ ] Database backups set up
- [ ] SSL/TLS certificates obtained
- [ ] Secrets rotated
- [ ] Security scan completed
- [ ] Performance testing done
- [ ] Load testing done
- [ ] Monitoring set up

## Backend Deployment

### Using Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker

Create a `Dockerfile` for the backend:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t checkin-backend .
docker run -p 8000:8000 --env-file .env checkin-backend
```

### Using Systemd

Create `/etc/systemd/system/checkin-backend.service`:

```ini
[Unit]
Description=CheckIn System Backend
After=network.target postgres.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/home/checkin/backend
Environment="PATH=/home/checkin/backend/venv/bin"
ExecStart=/home/checkin/backend/venv/bin/gunicorn \
    app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable checkin-backend
sudo systemctl start checkin-backend
```

## Frontend Deployment

### Static Build

```bash
cd frontend
npm run build
```

Upload the `dist/` folder to your web server.

### Using Nginx

Create `/etc/nginx/sites-available/checkin`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;

    root /var/www/checkin/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/checkin /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Using Docker

```dockerfile
# Build stage
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Database Setup

### PostgreSQL on Linux

```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE checkin_db;
CREATE USER checkin_user WITH PASSWORD 'strong_password';
ALTER ROLE checkin_user SET client_encoding TO 'utf8';
ALTER ROLE checkin_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE checkin_user SET default_transaction_deferrable TO on;
ALTER ROLE checkin_user SET default_transaction_read_committed To on;
GRANT ALL PRIVILEGES ON DATABASE checkin_db TO checkin_user;
\q
```

### Database Backups

Create a backup script `/usr/local/bin/backup-db.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/database"
mkdir -p $BACKUP_DIR

pg_dump -h localhost -U checkin_user -d checkin_db \
    > $BACKUP_DIR/checkin_db_$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql" -type f -mtime +30 -delete
```

Schedule with cron:

```bash
0 2 * * * /usr/local/bin/backup-db.sh
```

## Environment Variables

Create `.env.production`:

```
# Database
DATABASE_URL=postgresql://checkin_user:password@localhost:5432/checkin_db
SQLALCHEMY_ECHO=False

# JWT & Security
SECRET_KEY=generate-a-strong-random-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# App Settings
APP_NAME=CheckIn System
APP_VERSION=1.0.0
DEBUG=False
CORS_ORIGINS=["https://yourdomain.com"]

# Timezone
TIMEZONE=UTC

# Email (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## SSL/TLS Certificate

Using Let's Encrypt with Certbot:

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com
```

Auto-renewal:

```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## Monitoring & Logging

### Application Logging

Configure logging in backend:

```python
# app/core/logging.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

### System Monitoring

Using Prometheus and Grafana (optional):

1. Install Prometheus metrics library:
   ```bash
   pip install prometheus-client
   ```

2. Add to your FastAPI app:
   ```python
   from prometheus_client import Counter, make_wsgi_app
   
   REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests')
   ```

## Performance Optimization

### Caching

```python
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

# Configure Redis cache
```

### Database Connection Pooling

Already configured in `db/session.py`:

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True
)
```

### Frontend Optimization

- Enable gzip compression in Nginx
- Use CDN for static assets
- Implement service workers for offline support

## Security Considerations

1. **Secret Key**: Generate a strong random key using Python:
   ```python
   import secrets
   secrets.token_urlsafe(32)
   ```

2. **HTTPS**: Always use HTTPS in production

3. **CORS**: Restrict origins to only your domain

4. **Environment Variables**: Never commit `.env` files

5. **Database**: Use strong passwords, restrict IP access

6. **Rate Limiting**: Implement rate limiting for API endpoints

7. **SQL Injection**: Use ORM + parameterized queries (already implemented)

8. **XSS Protection**: Sanitize user inputs in frontend (Vue handles this)

## Rollback Plan

1. Keep previous version compiled and ready
2. Use blue-green deployment when possible
3. Database migration rollbacks:
   ```bash
   alembic downgrade -1
   ```

## Continuous Deployment

### Using GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        run: |
          ssh user@server 'cd /home/checkin && git pull && ./deploy.sh'
```

## Troubleshooting

### Application won't start
- Check logs: `journalctl -u checkin-backend -f`
- Check database connection
- Verify environment variables

### High memory usage
- Check for memory leaks in code
- Adjust worker count
- Monitor with `htop` or similar

### Database performance issues
- Run `ANALYZE` on tables
- Check for missing indexes
- Review slow query logs

## Support

For issues or questions about deployment, consult:
- FastAPI docs: https://fastapi.tiangolo.com/deployment/
- PostgreSQL docs: https://www.postgresql.org/docs/
- Nginx docs: https://nginx.org/en/docs/
