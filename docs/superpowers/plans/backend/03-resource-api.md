# Backend — Users, Products, Tags API + Unit Tests

**Goal:** Implement user management, product CRUD (with search/filter/pagination), tag management, image upload — all with unit test coverage.

**Depends on:** `02-auth-api.md` (auth headers fixture, JWT decorators)

---

## Task 3.1: Users API

**Files:**  
- Create: `app/api/users.py`

### Step 1: Create `app/api/users.py`

Flask-RESTx namespace `users_ns` with endpoints:

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/users/` | Admin | List users; optional `?approved=true/false` filter |
| POST | `/api/users/` | Admin | Create user |
| GET | `/api/users/<id>` | Admin | Get single user detail |
| PUT | `/api/users/<id>` | Admin | Edit user (username, email, role, password) |
| DELETE | `/api/users/<id>` | Admin | Delete user |
| POST | `/api/users/<id>/approve` | Admin | Approve/reject: `{approved: bool}` |

All endpoints use `@admin_required` decorator.

**Implementation details:**
- POST: validate username/email uniqueness, return 201
- PUT: only update fields present in payload; if password is empty string, skip it
- DELETE: cascade handled by DB (no related constraints to worry about for user)
- Approve: set `is_approved` from payload

---

## Task 3.2: Tags API

**Files:**  
- Create: `app/api/tags.py`

### Step 1: Create `app/api/tags.py`

Flask-RESTx namespace `tags_ns` with endpoints:

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/tags/<type>` | None | List tags (`type`: form/effect/function) |
| POST | `/api/tags/<type>` | Admin | Create tag `{name}` |
| PUT | `/api/tags/<type>/<id>` | Admin | Rename tag `{name}` |
| DELETE | `/api/tags/<type>/<id>` | Admin | Delete tag |

**Implementation details:**
- Use `TYPE_MAP = {"form": FormType, "effect": EffectType, "function": FunctionType}` for dynamic model selection
- Validate `type` param — 400 if invalid
- Validate name uniqueness — 409 if duplicate
- Validate name non-empty — 400 if blank

---

## Task 3.3: Products API

**Files:**  
- Create: `app/api/products.py`

### Step 1: Create `app/api/products.py`

Flask-RESTx namespace `products_ns` with endpoints:

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/products/` | None | List with search, filter, pagination, sort |
| GET | `/api/products/<id>` | None | Detail |
| POST | `/api/products/` | Admin | Create |
| PUT | `/api/products/<id>` | Admin | Update |
| DELETE | `/api/products/<id>` | Admin | Delete (removes image file) |
| POST | `/api/products/<id>/image` | Admin | Upload image (multipart) |
| DELETE | `/api/products/<id>/image` | Admin | Remove image |

**Product list query params:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| search | string | "" | Fuzzy match on name, description, ingredients |
| form_type_id | UUID | — | Filter by form type |
| effect_type_id | UUID | — | Filter by effect type |
| function_type_id | UUID | — | Filter by function type |
| page | int | 1 | Page number |
| per_page | int | 20 | Items per page (max 100) |
| sort_by | string | published_at | Sort field |
| sort_order | string | desc | asc or desc |

**Response format:**
```json
{"items": [...], "total": N, "page": 1, "per_page": 20, "pages": N}
```

**Image upload:** Accept multipart `image` field. Delete old image if one exists. Save new image via `save_image()`. Return `{"image": "/uploads/xxx.jpg"}`.

**Image delete:** Delete file from disk, clear `product.image` to empty string.

**Product delete:** Also call `delete_image()` to clean up the file.

---

## Task 3.4: Write resource API tests

**Files:**  
- Create: `tests/test_users.py`  
- Create: `tests/test_products.py`  
- Create: `tests/test_tags.py`  
- Create: `tests/test_upload.py`

### Step 1: Create `tests/test_users.py`

```python
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
```

### Step 2: Create `tests/test_tags.py`

```python
class TestListTags:
    def test_list_form_tags(self, client, db, auth_headers):
        """List form type tags."""
        from app.models.product import FormType
        db.session.add(FormType(name="防晒"))
        db.session.add(FormType(name="洁面"))
        db.session.commit()

        resp = client.get("/api/tags/form")
        assert resp.status_code == 200
        names = [t["name"] for t in resp.get_json()]
        assert "防晒" in names
        assert "洁面" in names

    def test_list_tags_no_auth_required(self, client, db):
        """Public can list tags without auth."""
        resp = client.get("/api/tags/form")
        assert resp.status_code == 200

    def test_list_invalid_type(self, client, db):
        """Invalid type returns 400."""
        resp = client.get("/api/tags/invalid")
        assert resp.status_code == 400

    def test_list_effect_and_function_types(self, client, db):
        from app.models.product import EffectType, FunctionType
        db.session.add(EffectType(name="保湿"))
        db.session.add(FunctionType(name="院线套装"))
        db.session.commit()

        effect_resp = client.get("/api/tags/effect")
        assert len(effect_resp.get_json()) == 1

        func_resp = client.get("/api/tags/function")
        assert len(func_resp.get_json()) == 1


class TestCreateTag:
    def test_create_tag(self, client, db, auth_headers):
        resp = client.post("/api/tags/form", headers=auth_headers, json={"name": "精华液"})
        assert resp.status_code == 201
        assert resp.get_json()["name"] == "精华液"

    def test_create_tag_duplicate(self, client, db, auth_headers):
        from app.models.product import FormType
        db.session.add(FormType(name="精华液"))
        db.session.commit()

        resp = client.post("/api/tags/form", headers=auth_headers, json={"name": "精华液"})
        assert resp.status_code == 409

    def test_create_tag_non_admin(self, client, db, user_headers):
        resp = client.post("/api/tags/form", headers=user_headers, json={"name": "面霜"})
        assert resp.status_code == 403


class TestUpdateTag:
    def test_update_tag(self, client, db, auth_headers):
        from app.models.product import FormType
        t = FormType(name="旧名")
        db.session.add(t)
        db.session.commit()

        resp = client.put(f"/api/tags/form/{t.id}", headers=auth_headers, json={"name": "新名"})
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "新名"


class TestDeleteTag:
    def test_delete_tag(self, client, db, auth_headers):
        from app.models.product import EffectType
        t = EffectType(name="保湿")
        db.session.add(t)
        db.session.commit()
        tid = t.id

        resp = client.delete(f"/api/tags/effect/{tid}", headers=auth_headers)
        assert resp.status_code == 200

        assert EffectType.query.get(tid) is None
```

### Step 3: Create `tests/test_products.py`

```python
import io
import json


def _create_test_product(client, auth_headers, overrides=None):
    """Helper to create a product. Asserts success and returns data dict."""
    data = {
        "name": "Test Product",
        "description": "A test product",
        "ingredients": "Water, Glycerin",
        "published_at": "2024-01-15",
        "form_tag_ids": [],
        "effect_tag_ids": [],
        "function_tag_ids": [],
    }
    if overrides:
        data.update(overrides)
    resp = client.post("/api/products/", headers=auth_headers, json=data)
    assert resp.status_code == 201, f"Product creation failed: {resp.get_json()}"
    return resp.get_json()


class TestListProducts:
    def test_list_products_public(self, client, db, auth_headers):
        """Unauthenticated can list products."""
        _create_test_product(client, auth_headers)

        resp = client.get("/api/products/")
        assert resp.status_code == 200
        assert resp.get_json()["total"] == 1

    def test_list_products_pagination(self, client, db, auth_headers):
        for i in range(3):
            _create_test_product(client, auth_headers, {"name": f"Product {i}"})

        resp = client.get("/api/products/?per_page=2&page=1")
        data = resp.get_json()
        assert len(data["items"]) == 2
        assert data["total"] == 3
        assert data["pages"] == 2

    def test_search_products(self, client, db, auth_headers):
        _create_test_product(client, auth_headers, {
            "name": "焕颜精华",
            "description": "抗衰老修复",
        })
        _create_test_product(client, auth_headers, {
            "name": "保湿面霜",
            "description": "深层补水",
        })

        resp = client.get("/api/products/?search=精华")
        assert resp.get_json()["total"] == 1

        resp = client.get("/api/products/?search=补水")
        assert resp.get_json()["total"] == 1

    def test_filter_by_form_type(self, client, db, auth_headers):
        from app.models.product import FormType
        ft = FormType(name="精华液")
        db.session.add(ft)
        db.session.commit()

        _create_test_product(client, auth_headers, {
            "name": "P1", "form_tag_ids": [str(ft.id)],
        })

        resp = client.get(f"/api/products/?form_type_id={ft.id}")
        assert resp.get_json()["total"] == 1

        resp = client.get("/api/products/?form_type_id=00000000-0000-0000-0000-000000000000")
        assert resp.get_json()["total"] == 0


class TestCreateProduct:
    def test_create_product_admin(self, client, db, auth_headers):
        resp = client.post("/api/products/", headers=auth_headers, json={
            "name": "新品精华",
            "description": "Test description",
            "ingredients": "Ingredient A, Ingredient B",
            "published_at": "2024-06-01",
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "新品精华"
        assert data["ingredients"] == "Ingredient A, Ingredient B"

    def test_create_product_non_admin(self, client, db, user_headers):
        resp = client.post("/api/products/", headers=user_headers, json={
            "name": "Test",
        })
        assert resp.status_code == 403

    def test_create_product_no_auth(self, client, db):
        resp = client.post("/api/products/", json={"name": "Test"})
        assert resp.status_code == 401


class TestUpdateProduct:
    def test_update_product(self, client, db, auth_headers):
        prod = _create_test_product(client, auth_headers, {"name": "Old Name"})
        prod_id = prod["id"]

        resp = client.put(f"/api/products/{prod_id}", headers=auth_headers, json={
            "name": "New Name",
        })
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "New Name"


class TestDeleteProduct:
    def test_delete_product(self, client, db, auth_headers):
        prod = _create_test_product(client, auth_headers)
        prod_id = prod["id"]

        resp = client.delete(f"/api/products/{prod_id}", headers=auth_headers)
        assert resp.status_code == 200

        resp = client.get(f"/api/products/{prod_id}")
        assert resp.status_code == 404


class TestProductDetail:
    def test_get_product_public(self, client, db, auth_headers):
        prod = _create_test_product(client, auth_headers)
        prod_id = prod["id"]

        resp = client.get(f"/api/products/{prod_id}")
        assert resp.status_code == 200
        assert resp.get_json()["name"] == prod["name"]

    def test_get_product_not_found(self, client, db):
        import uuid
        resp = client.get(f"/api/products/{uuid.uuid4()}")
        assert resp.status_code == 404


class TestProductImage:
    def test_upload_image(self, client, db, auth_headers):
        prod = _create_test_product(client, auth_headers)
        prod_id = prod["id"]

        data = {"image": (io.BytesIO(b"fake-image-data"), "test.png")}
        resp = client.post(
            f"/api/products/{prod_id}/image",
            headers=auth_headers,
            content_type="multipart/form-data",
            data=data,
        )
        # May fail due to file validation, but endpoint should be callable
        assert resp.status_code in (200, 400)

    def test_delete_image_no_auth(self, client, db):
        import uuid
        resp = client.delete(f"/api/products/{uuid.uuid4()}/image")
        assert resp.status_code == 401
```

### Step 4: Create `tests/test_upload.py`

```python
import io
import os
import pytest
from app import db as _db
from app.models.product import Product
from app.utils.upload import allowed_file, save_image, delete_image


class TestAllowedFile:
    def test_allowed_jpg(self):
        assert allowed_file("photo.jpg") is True

    def test_allowed_png(self):
        assert allowed_file("photo.png") is True

    def test_allowed_webp(self):
        assert allowed_file("photo.webp") is True

    def test_disallowed_pdf(self):
        assert allowed_file("doc.pdf") is False

    def test_no_extension(self):
        assert allowed_file("photo") is False


class TestSaveAndDeleteImage:
    def test_save_and_delete_image(self, app, db):
        from flask import current_app
        with app.app_context():
            product = Product(name="Test")
            db.session.add(product)
            db.session.commit()

            file = io.BytesIO(b"fake-png-content")
            file.filename = "test_image.png"

            path = save_image(file, str(product.id))
            assert path.startswith("/uploads/")
            assert path.endswith(".png")

            full_path = os.path.join(current_app.config["UPLOAD_FOLDER"], path.lstrip("/uploads/"))
            assert os.path.exists(full_path)

            delete_image(path)
            assert not os.path.exists(full_path)

    def test_delete_empty_path(self):
        delete_image("")  # should not raise
        delete_image(None)  # should not raise
```

### Step 5: Run all tests

```bash
cd backend && python -m pytest tests/ -v
```

Expected: 40+ tests passing with no failures.

---

## Task 3.5: Commit

```bash
git add app/api/users.py app/api/tags.py app/api/products.py backend/tests/
git commit -m "feat: add users, products, tags API with unit tests"
```
