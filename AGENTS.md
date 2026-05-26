# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## 开发规范

- Git commit message 使用中文

## Project Overview

化妆品产品管理平台 (Skincare Product Platform) — 产品展示 + 管理后台。两个角色：管理员（产品上传/编辑/删除、用户管理、标签管理）和普通用户（查看/搜索）。JWT 认证，用户注册需管理员审核。

## Development Commands

### Backend (Flask)

```bash
# Install deps (venv already at ./venv)
./venv/Scripts/pip install -r requirements.txt

# Run dev server
./venv/Scripts/python main.py

# Run all tests (uses SQLite in-memory, no PG needed)
./venv/Scripts/python -m pytest tests/ -v

# Run single test
./venv/Scripts/python -m pytest tests/test_auth.py::TestLogin::test_login_success -v

# Database migration
./venv/Scripts/flask db migrate -m "description"
./venv/Scripts/flask db upgrade

# Create admin user
./venv/Scripts/flask create-admin --username admin --email admin@test.com --password xxx

# Seed default function tags
./venv/Scripts/flask seed-tags
```

### Frontend (Vue 3)

```bash
cd frontend

# Install deps
npm install

# Run dev server (proxies /api to localhost:5000)
npm run dev

# Build for production
npm run build
```

### PostgreSQL Connection

- User: `app`, Password: `password`, DB: `skincare`, Port: 5432
- Config in `config.py` (overridable via `.env`)

### Docker

```bash
# Build and start
docker compose up -d --build

# View logs
docker compose logs -f backend

# Stop
docker compose down
```

## Backend Architecture

Flask + Flask-RESTx layered structure:

```
app/
├── api/            # Flask-RESTx namespaces (auth, users, products, tags)
├── auth/           # JWT decorators (jwt_required, admin_required)
├── models/         # SQLAlchemy models (User, Product, Tag)
├── utils/          # upload.py (file upload/delete helpers)
├── cli.py          # Flask CLI commands (create-admin, seed-tags)
└── __init__.py     # App factory, DB init, API setup, SPA fallback routes
```

**Key patterns:**
- All admin endpoints use `@admin_required` decorator
- Public endpoints (product list, tag list, product detail) require no auth
- UUID primary keys stored as `db.String(36)` (compatible with both SQLite and PostgreSQL)
- Flask-Migrate (Alembic) for migrations
- Date strings from API are converted via `_parse_date()` helper
- Image uploads stored in `UPLOAD_FOLDER` (Docker volume), served via `/uploads/`

**API prefix:** `/api/`

## Frontend Architecture

Vue 3 + Element Plus + Pinia + Vue Router:

```
frontend/src/
├── api/            # Axios instance + API modules (auth, products, users, tags)
├── components/     # Shared components (ProductCard, FilterChips, ImageUpload)
├── router/         # Vue Router with JWT auth guards
├── store/          # Pinia stores (auth, products, users, tags)
└── views/
    ├── public/     # Home.vue, ProductDetail.vue (product showcase)
    └── admin/      # AdminLogin, AdminLayout, Dashboard, ProductList/Form, UserList/Form, TagManage
```

**Key patterns:**
- JWT token stored in localStorage, attached via Axios interceptor
- 401 responses auto-redirect to /admin/login
- Admin routes protected by `meta.requiresAuth` + `meta.requiresAdmin` guards
- Primary theme color: `#1a56a8` (Rhine Blue)

## Design Specs

- `docs/superpowers/specs/2026-05-24-admin-management-design.md` — full system design spec
- `docs/superpowers/plans/` — implementation plans (7 files: 3 backend, 3 frontend, 1 deployment)

## Deployment

Production uses a **multi-stage Docker build**:
1. Stage 1 (Node): builds Vue SPA → `dist/`
2. Stage 2 (Python): copies `dist/` into Flask's `static/` directory
3. Flask serves both API (`/api/*`) and SPA (`/*`) on port 5000
4. PostgreSQL 16 runs as a separate container
