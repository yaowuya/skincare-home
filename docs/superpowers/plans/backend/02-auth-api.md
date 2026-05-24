# Backend — Auth API + JWT + Unit Tests

**Goal:** Implement JWT-based authentication (register, login, me, change password) with complete unit test coverage.

**Depends on:** `01-core-skeleton.md` (models, decorators, CLI)

---

## Task 2.1: Auth API namespace

**Files:**  
- Create: `app/api/auth.py`

### Step 1: Create `app/api/auth.py`

Flask-RESTx namespace `auth_ns` with four endpoints:

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | None | Register new user (is_approved=false) |
| POST | `/api/auth/login` | None | Returns `{access_token, user}` |
| GET | `/api/auth/me` | JWT | Current user profile |
| PUT | `/api/auth/password` | JWT | Change password (requires old_password + new_password) |

**Register:**
- Input: `{username, email, password}`
- 201: Returns `{message: "Registration successful, awaiting admin approval"}`
- 409: Username or email already exists

**Login:**
- Input: `{username, password}`
- 200: `{access_token: "eyJ...", user: {...}}`
- 401: Invalid credentials
- 403: Account not approved yet

**/me:**
- Uses `@jwt_required` decorator
- Returns `g.current_user.to_dict()`

**/password:**
- Input: `{old_password, new_password}`
- 400: Old password is incorrect
- 200: `{message: "Password updated"}`

---

## Task 2.2: Test infrastructure

**Files:**  
- Create: `tests/conftest.py`  
- Create: `tests/__init__.py`

### Step 1: Create `tests/__init__.py`

Empty file.

### Step 2: Create `tests/conftest.py`

```python
import pytest
from app import create_app, db as _db
from config import TestingConfig


@pytest.fixture(scope="session")
def app():
    """Create application with TestingConfig."""
    application = create_app(TestingConfig)
    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    """Provide clean database per test."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Test client."""
    return app.test_client()


@pytest.fixture(scope="function")
def auth_headers(client, db):
    """Create an approved admin user and return auth header dict."""
    from app.models.user import User
    user = User(username="admin", email="admin@test.com", role="admin", is_approved=True)
    user.set_password("admin123")
    db.session.add(user)
    db.session.commit()

    resp = client.post("/api/auth/login", json={
        "username": "admin", "password": "admin123",
    })
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def user_headers(client, db):
    """Create an approved regular user and return auth header dict."""
    from app.models.user import User
    user = User(username="user", email="user@test.com", role="user", is_approved=True)
    user.set_password("user123")
    db.session.add(user)
    db.session.commit()

    resp = client.post("/api/auth/login", json={
        "username": "user", "password": "user123",
    })
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

---

## Task 2.3: Write auth unit tests

**Files:**  
- Create: `tests/test_auth.py`

### Step 1: Create `tests/test_auth.py`

```python
import pytest
from app.models.user import User


class TestRegister:
    def test_register_success(self, client, db):
        resp = client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "new@test.com",
            "password": "pass123",
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert "awaiting admin approval" in data["message"]

        # User is created in DB
        user = User.query.filter_by(username="newuser").first()
        assert user is not None
        assert user.is_approved is False
        assert user.role == "user"

    def test_register_duplicate_username(self, client, db):
        u = User(username="dup", email="first@test.com", is_approved=True)
        u.set_password("x")
        db.session.add(u)
        db.session.commit()

        resp = client.post("/api/auth/register", json={
            "username": "dup",
            "email": "other@test.com",
            "password": "pass123",
        })
        assert resp.status_code == 409
        assert "already exists" in resp.get_json()["message"]

    def test_register_duplicate_email(self, client, db):
        u = User(username="first", email="dup@test.com", is_approved=True)
        u.set_password("x")
        db.session.add(u)
        db.session.commit()

        resp = client.post("/api/auth/register", json={
            "username": "second",
            "email": "dup@test.com",
            "password": "pass123",
        })
        assert resp.status_code == 409

    def test_register_missing_fields(self, client, db):
        resp = client.post("/api/auth/register", json={"username": "x"})
        assert resp.status_code == 400  # validation error


class TestLogin:
    def test_login_success(self, client, db):
        u = User(username="testuser", email="test@test.com", is_approved=True)
        u.set_password("secret")
        db.session.add(u)
        db.session.commit()

        resp = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "secret",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "access_token" in data
        assert data["user"]["username"] == "testuser"
        assert data["user"]["role"] == "user"

    def test_login_wrong_password(self, client, db):
        u = User(username="testuser", email="test@test.com", is_approved=True)
        u.set_password("secret")
        db.session.add(u)
        db.session.commit()

        resp = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "wrong",
        })
        assert resp.status_code == 401

    def test_login_not_approved(self, client, db):
        u = User(username="pending", email="pending@test.com", is_approved=False)
        u.set_password("secret")
        db.session.add(u)
        db.session.commit()

        resp = client.post("/api/auth/login", json={
            "username": "pending",
            "password": "secret",
        })
        assert resp.status_code == 403
        assert "approved" in resp.get_json()["message"]

    def test_login_nonexistent_user(self, client, db):
        resp = client.post("/api/auth/login", json={
            "username": "ghost",
            "password": "x",
        })
        assert resp.status_code == 401


class TestMe:
    def test_me_success(self, client, db, auth_headers):
        resp = client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["username"] == "admin"

    def test_me_no_token(self, client, db):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_me_invalid_token(self, client, db):
        resp = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid"})
        assert resp.status_code == 401


class TestChangePassword:
    def test_change_password_success(self, client, db, auth_headers):
        resp = client.put("/api/auth/password", headers=auth_headers, json={
            "old_password": "admin123",
            "new_password": "newadmin123",
        })
        assert resp.status_code == 200
        assert resp.get_json()["message"] == "Password updated"

        # Verify can login with new password
        resp = client.post("/api/auth/login", json={
            "username": "admin",
            "password": "newadmin123",
        })
        assert resp.status_code == 200

    def test_change_password_wrong_old(self, client, db, auth_headers):
        resp = client.put("/api/auth/password", headers=auth_headers, json={
            "old_password": "wrong",
            "new_password": "newadmin123",
        })
        assert resp.status_code == 400

    def test_change_password_no_auth(self, client, db):
        resp = client.put("/api/auth/password", json={
            "old_password": "x",
            "new_password": "y",
        })
        assert resp.status_code == 401
```

### Step 2: Run tests and verify

```bash
cd backend && python -m pytest tests/test_auth.py -v
```

Expected: All tests pass (16+ tests).

---

## Task 2.4: Commit

```bash
git add app/api/auth.py backend/tests/
git commit -m "feat: add auth API with JWT and unit tests"
```
