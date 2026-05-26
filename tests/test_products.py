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
        from app.models.product import Tag, TagType
        ft = Tag(name="精华液", type=TagType.form)
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
    def test_upload_multiple_images_appends(self, client, db, auth_headers):
        prod = _create_test_product(client, auth_headers)
        prod_id = prod["id"]

        first = client.post(
            f"/api/products/{prod_id}/image",
            headers=auth_headers,
            content_type="multipart/form-data",
            data={"image": (io.BytesIO(b"first-image-data"), "first.png")},
        )
        second = client.post(
            f"/api/products/{prod_id}/image",
            headers=auth_headers,
            content_type="multipart/form-data",
            data={"image": (io.BytesIO(b"second-image-data"), "second.png")},
        )

        assert first.status_code == 200
        assert second.status_code == 200

        detail = client.get(f"/api/products/{prod_id}")
        data = detail.get_json()
        assert len(data["images"]) == 2
        assert data["image"] == data["images"][0]["url"]
        assert data["images"][0]["sort_order"] == 0
        assert data["images"][1]["sort_order"] == 1

    def test_delete_single_image(self, client, db, auth_headers):
        prod = _create_test_product(client, auth_headers)
        prod_id = prod["id"]

        client.post(
            f"/api/products/{prod_id}/image",
            headers=auth_headers,
            content_type="multipart/form-data",
            data={"image": (io.BytesIO(b"first-image-data"), "first.png")},
        )
        second = client.post(
            f"/api/products/{prod_id}/image",
            headers=auth_headers,
            content_type="multipart/form-data",
            data={"image": (io.BytesIO(b"second-image-data"), "second.png")},
        ).get_json()

        resp = client.delete(
            f"/api/products/{prod_id}/images/{second['id']}",
            headers=auth_headers,
        )

        assert resp.status_code == 200
        detail = client.get(f"/api/products/{prod_id}").get_json()
        assert len(detail["images"]) == 1
        assert detail["images"][0]["id"] != second["id"]

    def test_delete_image_no_auth(self, client, db):
        import uuid
        resp = client.delete(f"/api/products/{uuid.uuid4()}/image")
        assert resp.status_code == 401
