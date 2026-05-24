# Skincare Product Platform — Management System Design

**Date:** 2026-05-24
**Status:** Approved
**Deployment:** Docker on Tencent Cloud

---

## 1. Architecture Overview

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3 + Element Plus + Pinia + Vue Router |
| Backend | Flask + Flask-RESTx + SQLAlchemy |
| Database | PostgreSQL 16 |
| Auth | JWT (PyJWT) |
| Deployment | Docker Compose (single-server, Tencent Cloud) |

### Deployment Model (Single Container)

Production deployment uses a **multi-stage Docker build**:
1. **Stage 1 (Node)** — Build Vue SPA producing `dist/`
2. **Stage 2 (Python)** — Copy `dist/` into Flask's static directory, Flask serves both API and SPA

Flow: `N/A` (no Nginx) → Flask (Gunicorn, `:5000`) handles all routes:
- `/api/*` → REST API
- `/*` → Vue SPA (Flask fallback route via `send_from_directory`)
- `/uploads/*` → Flask static file serving from Docker volume

### Project Structure

```
skincare-home/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # create_app(), register blueprints
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   └── tag.py
│   │   ├── api/
│   │   │   ├── auth.py          # register / login / me
│   │   │   ├── users.py         # admin user CRUD
│   │   │   ├── products.py      # product CRUD + image upload
│   │   │   └── tags.py          # tag CRUD (3 types)
│   │   ├── auth/
│   │   │   └── decorators.py    # JWT required, admin required
│   │   └── utils/
│   │       └── upload.py        # file upload helper
│   ├── config.py                # Flask config (env-based)
│   ├── requirements.txt
│   ├── Dockerfile               # multi-stage (Node → Python)
│   └── entrypoint.sh
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios instance + API modules
│   │   │   ├── auth.js
│   │   │   ├── products.js
│   │   │   ├── users.js
│   │   │   └── tags.js
│   │   ├── views/
│   │   │   ├── public/
│   │   │   │   ├── Home.vue         # Product showcase (replaces demo.html)
│   │   │   │   └── ProductDetail.vue # Modal-based detail
│   │   │   └── admin/
│   │   │       ├── AdminLogin.vue
│   │   │       ├── AdminLayout.vue   # Sidebar layout
│   │   │       ├── Dashboard.vue
│   │   │       ├── ProductList.vue
│   │   │       ├── ProductForm.vue
│   │   │       ├── UserList.vue
│   │   │       ├── UserForm.vue
│   │   │       └── TagManage.vue
│   │   ├── router/
│   │   │   └── index.js
│   │   ├── store/
│   │   │   ├── auth.js
│   │   │   ├── products.js
│   │   │   ├── users.js
│   │   │   └── tags.js
│   │   ├── components/
│   │   │   ├── ProductCard.vue
│   │   │   ├── FilterChips.vue
│   │   │   └── ImageUpload.vue
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 2. Database Schema

### Tables

#### `users`
| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PK, default gen_random_uuid() |
| username | VARCHAR(80) | UNIQUE, NOT NULL |
| email | VARCHAR(120) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(256) | NOT NULL |
| role | VARCHAR(20) | NOT NULL, default 'user' (enum: admin/user) |
| is_approved | BOOLEAN | default false |
| created_at | TIMESTAMP | default now() |
| updated_at | TIMESTAMP | default now(), onupdate now() |

#### `products`
| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PK |
| name | VARCHAR(200) | NOT NULL |
| description | TEXT | |
| ingredients | TEXT | |
| image | VARCHAR(300) | |
| published_at | DATE | |
| created_by | UUID | FK → users.id |
| created_at | TIMESTAMP | default now() |
| updated_at | TIMESTAMP | default now() |

#### `form_types`
| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PK |
| name | VARCHAR(50) | UNIQUE, NOT NULL |

#### `effect_types`
| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PK |
| name | VARCHAR(50) | UNIQUE, NOT NULL |

#### `function_types`
| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PK |
| name | VARCHAR(50) | UNIQUE, NOT NULL |

#### `product_form_tags`
| Column | Type | Constraints |
|--------|------|------------|
| product_id | UUID | FK → products.id, ON DELETE CASCADE |
| form_type_id | UUID | FK → form_types.id, ON DELETE CASCADE |

#### `product_effect_tags`
| Column | Type | Constraints |
|--------|------|------------|
| product_id | UUID | FK → products.id, ON DELETE CASCADE |
| effect_type_id | UUID | FK → effect_types.id, ON DELETE CASCADE |

#### `product_function_tags`
| Column | Type | Constraints |
|--------|------|------------|
| product_id | UUID | FK → products.id, ON DELETE CASCADE |
| function_type_id | UUID | FK → function_types.id, ON DELETE CASCADE |

### Initial `function_types` seed data
1. 问题性肌肤修复
2. 轻医美护肤
3. 功效猛药/药妆类
4. 院线套装
5. 电商爆款
6. 婴童护肤
7. 底妆彩妆类

---

## 3. API Design (Flask-RESTx Namespaces)

### Auth (`/api/auth`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/register` | None | User registration |
| POST | `/login` | None | Returns JWT access_token |
| GET | `/me` | JWT | Current user profile |

### Users (`/api/users`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | Admin | List all users, filter by approved status |
| POST | `/` | Admin | Create new user |
| PUT | `/:id` | Admin | Edit user |
| DELETE | `/:id` | Admin | Delete user |
| POST | `/:id/approve` | Admin | Approve/reject user |

### Products (`/api/products`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | None | List products (public); query params: search, form_type_id, effect_type_id, function_type_id |
| GET | `/:id` | None | Product detail (public) |
| POST | `/` | Admin | Create product |
| PUT | `/:id` | Admin | Update product |
| DELETE | `/:id` | Admin | Delete product |
| POST | `/:id/image` | Admin | Upload product image (multipart) |

### Tags (`/api/tags`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/:type` | None | List tags by type (form/effect/function) |
| POST | `/:type` | Admin | Create tag |
| PUT | `/:type/:id` | Admin | Update tag name |
| DELETE | `/:type/:id` | Admin | Delete tag |

---

## 4. Frontend Route & Page Design

### Routes
```
/                    → Home.vue            (public)
/products/:id        → ProductDetail.vue   (public)
/admin/login         → AdminLogin.vue
/admin               → redirect to /admin/dashboard
/admin/dashboard     → Dashboard.vue       (admin, JWT guard)
/admin/products      → ProductList.vue     (admin)
/admin/products/new  → ProductForm.vue     (admin)
/admin/products/:id/edit → ProductForm.vue (admin)
/admin/users         → UserList.vue        (admin only)
/admin/users/new     → UserForm.vue        (admin only)
/admin/users/:id/edit → UserForm.vue       (admin only)
/admin/tags          → TagManage.vue       (admin only)
```

### State Management (Pinia)

**authStore** — token, user profile, login/logout, permission checks
**productStore** — product list, pagination, filters, CRUD operations
**userStore** — user list, approval, CRUD (admin scope)
**tagStore** — three tag type lists, CRUD

### Key Page Details

#### Home.vue (Public Showcase)
- Hero + filter chips (form / effect / function) + product masonry grid
- ProductCard component with hover effect
- ProductDetail modal with image carousel
- Data fetched from `GET /api/products`

#### ProductList.vue (Admin)
- Search input + 3-row filter chips + Element Plus `<el-table>`
- Columns: image thumbnail, name, tags, published date, actions (edit/delete)
- Pagination via `el-pagination`

#### ProductForm.vue (Admin Create/Edit)
- Name, description, ingredients (extensible tag input), published date
- 3 multi-select tag pickers (form / effect / function categories)
- Image upload with preview
- Save/Cancel buttons

#### UserList.vue (Admin)
- `<el-table>` with username, email, role, approved status, created date
- Actions: approve/reject (for pending), edit, delete
- Bulk actions or per-row buttons

#### TagManage.vue (Admin)
- Three sections (form / effect / function), each with tag list + add/rename/delete

---

## 5. Auth & RBAC

- **JWT flow:** Login → returns `access_token` → stored in `localStorage` → Axios interceptor attaches `Authorization: Bearer <token>` to all requests
- **Role check:** Flask decorator `@admin_required` on admin-only endpoints; Vue Router `beforeEach` guard checks role from `authStore`
- **Registration → Approval flow:** New user `is_approved = false` → Admin sees pending users in UserList → Admin approves → User can login and access basic view/search

---

## 6. Image Upload

- Upload endpoint: `POST /api/products/:id/image`
- Server stores to Docker volume path `/app/uploads/`
- Flask serves `/uploads/*` as static files
- Frontend: El-upload component with preview, max 1 image per product
- Allowed types: jpg, png, webp

---

## 7. Docker Deployment

### `docker-compose.yml`
```yaml
services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://app:password@postgres:5432/skincare
      - SECRET_KEY=...
      - UPLOAD_FOLDER=/app/uploads
    volumes:
      - uploads:/app/uploads
    depends_on:
      - postgres

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: skincare
      POSTGRES_USER: app
      POSTGRES_PASSWORD: password
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
  uploads:
```

### `Dockerfile` (Multi-stage)
```dockerfile
# Stage 1: Build Vue
FROM node:20-alpine AS frontend
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend
FROM python:3.12-slim
WORKDIR /app
COPY --from=frontend /app/dist /app/static
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
```
