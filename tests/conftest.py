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
    """Provide clean database per test function."""
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
    from app.models.user import User, RoleEnum
    # Ensure clean state - check if admin exists first
    user = User.query.filter_by(username="admin").first()
    if not user:
        user = User(username="admin", email="admin@test.com", role=RoleEnum.admin, is_approved=True)
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
    from app.models.user import User, RoleEnum
    user = User.query.filter_by(username="user").first()
    if not user:
        user = User(username="user", email="user@test.com", role=RoleEnum.user, is_approved=True)
        user.set_password("user123")
        db.session.add(user)
        db.session.commit()

    resp = client.post("/api/auth/login", json={
        "username": "user", "password": "user123",
    })
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
