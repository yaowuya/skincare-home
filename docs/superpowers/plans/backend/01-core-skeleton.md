# Backend — Core Skeleton

**Goal:** Set up Flask project structure, app factory, config with .env, database models, CLI commands, and verify it runs.

**Prerequisites:** None (this is the first task).

---

## Task 1.1: Project structure

**Files:**  
- Create: `app/__init__.py`  
- Create: `config.py`  
- Create: `requirements.txt`

### Step 1: Verify backend directory exists

```bash
ls backend/
```

Expected: `app/  config.py  requirements.txt` and subdirectories already exist.

### Step 2: Update `requirements.txt`

```text
flask==3.1.1
flask-restx==1.3.0
flask-sqlalchemy==3.1.1
flask-migrate==4.1.0
flask-cors==5.0.1
psycopg2-binary==2.9.10
PyJWT==2.10.1
python-dotenv==1.1.0
Pillow==11.2.1
gunicorn==23.0.0
werkzeug==3.1.3
# Testing
pytest==8.3.5
pytest-flask==1.3.0
```

### Step 3: Verify/update `config.py`

```python
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
load_dotenv(dotenv_path)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "postgresql://app:password@localhost:5432/skincare")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join(os.getcwd(), "uploads"))
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024))
    JWT_SECRET = os.environ.get("JWT_SECRET", Config.SECRET_KEY)
    JWT_EXPIRATION_HOURS = int(os.environ.get("JWT_EXPIRATION_HOURS", 24))
    JSON_AS_ASCII = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    UPLOAD_FOLDER = "/tmp/test-uploads"
    JWT_SECRET = "test-secret"
```

Note: `Config.SECRET_KEY` reference in JWT_SECRET is a forward reference — replace `Config.SECRET_KEY` with just `SECRET_KEY` since it's inside the class:

```python
JWT_SECRET = os.environ.get("JWT_SECRET", SECRET_KEY)
```

### Step 4: Create `.env` (project root)

```bash
cat > .env << 'EOF'
DATABASE_URL=postgresql://app:password@localhost:5432/skincare
SECRET_KEY=dev-secret-change-in-prod
JWT_SECRET=
JWT_EXPIRATION_HOURS=24
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=5242880
FLASK_ENV=development
EOF
```

### Step 5: Verify `app/__init__.py` app factory

Ensure it contains:
- `create_app(config_object=None)` that loads Config by default
- `db = SQLAlchemy()`, `migrate = Migrate()` at module level
- Flask-RESTx Api with prefix `/api`
- Imports and registers 4 namespaces: auth, users, products, tags
- Serves Vue SPA from `static/` directory
- CORS enabled
- Upload directory created on startup

### Step 6: Install dependencies and verify

```bash
cd backend && pip install -r requirements.txt && python -c "from app import create_app; app = create_app(); print('OK')"
```

Expected: `OK` with no errors.

---

## Task 1.2: Database models

**Files:**  
- Create: `app/models/__init__.py`  
- Create: `app/models/user.py`  
- Create: `app/models/product.py`

### Step 1: Create `app/models/user.py`

```python
import uuid
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")   # admin | user
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_approved": self.is_approved,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
```

### Step 2: Create `app/models/product.py`

Contains five models: `Product`, `FormType`, `EffectType`, `FunctionType` plus three association tables (`product_form_tags`, `product_effect_tags`, `product_function_tags`).

Each tag model has: `id (UUID PK)`, `name (String 50, UNIQUE)`, `to_dict()`.

Product model has: `id, name, description, ingredients, image, published_at, created_by (FK), created_at, updated_at`. Relationships: `form_tags`, `effect_tags`, `function_tags` via `db.relationship(secondary=...)` with `lazy="selectin"`.

`to_dict()` returns all fields plus nested tag lists.

### Step 3: Create `app/models/__init__.py`

```python
from app.models.user import User
from app.models.product import Product, FormType, EffectType, FunctionType

__all__ = ["User", "Product", "FormType", "EffectType", "FunctionType"]
```

### Step 4: Verify models import

```bash
cd backend && python -c "from app.models import User, Product, FormType, EffectType, FunctionType; print('Models OK')"
```

Expected: No import errors.

---

## Task 1.3: Auth decorators + CLI commands + Upload utils

**Files:**  
- Create: `app/auth/decorators.py`  
- Create: `app/cli.py`  
- Create: `app/utils/upload.py`

### Step 1: `app/auth/decorators.py`

Must export:
- `generate_token(user_id)` — creates HS256 JWT with `user_id`, `exp`, `iat`
- `decode_token(token)` — decodes and validates JWT
- `jwt_required(f)` — Flask view decorator that reads `Authorization: Bearer <token>`, sets `g.current_user`
- `admin_required(f)` — chains `@jwt_required` then checks `g.current_user.role == "admin"`

Error cases:
- 401: Missing/expired/invalid token
- 403: Non-admin user hits admin endpoint

### Step 2: `app/cli.py`

Two click commands registered via `register_commands(app)`:
- `flask create-admin --username --email --password` — creates admin user (idempotent)
- `flask seed-tags` — seeds 7 default `FunctionType` rows

### Step 3: `app/utils/upload.py`

Must export:
- `allowed_file(filename)` — checks jpg/png/webp extension
- `save_image(file, product_id)` — saves to `UPLOAD_FOLDER`, returns `/uploads/<name>`
- `delete_image(image_path)` — removes file from disk, no-op if path empty

---

## Task 1.4: Commit

```bash
git add  .env
git commit -m "feat: add Flask backend skeleton with models and config"
```
