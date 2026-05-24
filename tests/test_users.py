import pytest
from app.models.user import User


class TestListUsers:
    def test_list_users_admin(self, client, db, auth_headers):
        """Admin can list users."""
        u = User(username="user1", email="u1@test.com", role="user", is_approved=True)
        u.set_password("x")
        db.session.add(u)
        db.session.commit()

        resp = client.get("/api/users/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) >= 1
        usernames = [u["username"] for u in data]
        assert "admin" in usernames
        assert "user1" in usernames

    def test_list_users_filter_approved(self, client, db, auth_headers):
        """Filter by approved status."""
        u = User(username="pending_u", email="p@test.com", role="user", is_approved=False)
        u.set_password("x")
        db.session.add(u)
        db.session.commit()

        resp = client.get("/api/users/?approved=false", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        for u in data:
            assert u["is_approved"] is False

    def test_list_users_non_admin(self, client, db, user_headers):
        """Regular user gets 403."""
        resp = client.get("/api/users/", headers=user_headers)
        assert resp.status_code == 403

    def test_list_users_no_auth(self, client, db):
        """Unauthenticated gets 401."""
        resp = client.get("/api/users/")
        assert resp.status_code == 401


class TestCreateUser:
    def test_create_user_success(self, client, db, auth_headers):
        """Admin creates a user."""
        resp = client.post("/api/users/", headers=auth_headers, json={
            "username": "newguy",
            "email": "new@test.com",
            "password": "pass123",
            "role": "user",
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["username"] == "newguy"

        user = User.query.filter_by(username="newguy").first()
        assert user is not None

    def test_create_user_duplicate(self, client, db, auth_headers):
        """Duplicate username returns 409."""
        u = User(username="existing", email="ex@test.com", role="user", is_approved=True)
        u.set_password("x")
        db.session.add(u)
        db.session.commit()

        resp = client.post("/api/users/", headers=auth_headers, json={
            "username": "existing",
            "email": "other@test.com",
            "password": "x",
        })
        assert resp.status_code == 409


class TestUpdateUser:
    def test_update_user_success(self, client, db, auth_headers):
        """Admin updates user fields."""
        u = User(username="oldname", email="old@test.com", role="user", is_approved=True)
        u.set_password("x")
        db.session.add(u)
        db.session.commit()

        resp = client.put(f"/api/users/{u.id}", headers=auth_headers, json={
            "username": "newname",
            "role": "admin",
        })
        assert resp.status_code == 200
        assert resp.get_json()["username"] == "newname"
        assert resp.get_json()["role"] == "admin"


class TestDeleteUser:
    def test_delete_user_success(self, client, db, auth_headers):
        u = User(username="goner", email="gone@test.com", role="user", is_approved=True)
        u.set_password("x")
        db.session.add(u)
        db.session.commit()
        uid = u.id

        resp = client.delete(f"/api/users/{uid}", headers=auth_headers)
        assert resp.status_code == 200

        assert User.query.get(uid) is None

    def test_delete_nonexistent(self, client, db, auth_headers):
        import uuid
        resp = client.delete(f"/api/users/{uuid.uuid4()}", headers=auth_headers)
        assert resp.status_code == 404


class TestApproveUser:
    def test_approve_user(self, client, db, auth_headers):
        u = User(username="pending", email="pend@test.com", role="user", is_approved=False)
        u.set_password("x")
        db.session.add(u)
        db.session.commit()

        resp = client.post(f"/api/users/{u.id}/approve", headers=auth_headers, json={
            "approved": True,
        })
        assert resp.status_code == 200
        assert resp.get_json()["is_approved"] is True

    def test_reject_user(self, client, db, auth_headers):
        u = User(username="pending2", email="pend2@test.com", role="user", is_approved=True)
        u.set_password("x")
        db.session.add(u)
        db.session.commit()

        resp = client.post(f"/api/users/{u.id}/approve", headers=auth_headers, json={
            "approved": False,
        })
        assert resp.status_code == 200
        assert resp.get_json()["is_approved"] is False
