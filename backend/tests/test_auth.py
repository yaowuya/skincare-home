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
