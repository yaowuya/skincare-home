# Docker Deployment Configuration

**Goal:** Create multi-stage Docker build, docker-compose, and entrypoint for production deployment on Tencent Cloud.

**Depends on:** All backend + frontend tasks complete.

---

## Task D1: Docker configuration files

**Files:**  
- Create: `backend/Dockerfile`  
- Create: `backend/entrypoint.sh`  
- Create: `docker-compose.yml`  
- Create: `.env.example`  
- Modify: `.gitignore`

### Step 1: `backend/Dockerfile` (multi-stage)

```dockerfile
# Stage 1: Build Vue frontend
FROM node:22-alpine AS frontend
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend
FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
COPY --from=frontend /app/dist /app/static

RUN chmod +x entrypoint.sh

EXPOSE 5000
ENTRYPOINT ["./entrypoint.sh"]
```

### Step 2: `backend/entrypoint.sh`

```bash
#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
while ! nc -z postgres 5432; do sleep 1; done
echo "PostgreSQL ready."

flask db upgrade
flask seed-tags
flask create-admin --username admin --email admin@example.com --password admin123 2>/dev/null || true

exec gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### Step 3: `docker-compose.yml`

```yaml
services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "5000:5000"
    env_file: .env
    environment:
      - DATABASE_URL=postgresql://app:${DB_PASSWORD:-password}@postgres:5432/skincare
    volumes:
      - uploads:/app/uploads
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: skincare
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${DB_PASSWORD:-password}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d skincare"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  pgdata:
  uploads:
```

### Step 4: `.env.example`

```bash
# Database
DB_PASSWORD=changeme

# Flask
SECRET_KEY=generate-a-random-secret-key
JWT_EXPIRATION_HOURS=24
FLASK_ENV=production

# Upload
MAX_CONTENT_LENGTH=5242880
```

### Step 5: Update `.gitignore`

```gitignore
__pycache__/
*.pyc
venv/
.venv/
node_modules/
frontend/dist/
.env
uploads/*
.idea/
.vscode/
*.swp
.DS_Store
Thumbs.db
```

---

## Task D2: Verify build

### Step 1: Build and test

```bash
# Copy .env.example to .env for production
cp .env.example .env

# Build Docker image
docker compose build

# Start services
docker compose up -d

# Check logs
docker compose logs -f backend
```

Expected: Backend starts, PostgreSQL connects, migrations run, admin created, Gunicorn listening on 0.0.0.0:5000.

### Step 2: Smoke test

```bash
# Test API responds
curl http://localhost:5000/api/products/

# Test Vue SPA is served
curl http://localhost:5000/ | head -5
```

Expected: API returns JSON, SPA returns HTML.

---

## Task D3: Commit

```bash
git add backend/Dockerfile backend/entrypoint.sh docker-compose.yml .env.example .gitignore
git commit -m "feat: add Docker deployment configuration"
```
