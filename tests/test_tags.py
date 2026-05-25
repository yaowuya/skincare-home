import pytest
from app.models.product import Tag, TagType


class TestListTags:
    def test_list_form_tags(self, client, db, auth_headers):
        """List form type tags."""
        db.session.add(Tag(name="防晒", type=TagType.form))
        db.session.add(Tag(name="洁面", type=TagType.form))
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
        db.session.add(Tag(name="保湿", type=TagType.effect))
        db.session.add(Tag(name="院线套装", type=TagType.function))
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
        db.session.add(Tag(name="精华液", type=TagType.form))
        db.session.commit()

        resp = client.post("/api/tags/form", headers=auth_headers, json={"name": "精华液"})
        assert resp.status_code == 409

    def test_create_tag_non_admin(self, client, db, user_headers):
        resp = client.post("/api/tags/form", headers=user_headers, json={"name": "面霜"})
        assert resp.status_code == 403


class TestUpdateTag:
    def test_update_tag(self, client, db, auth_headers):
        t = Tag(name="旧名", type=TagType.form)
        db.session.add(t)
        db.session.commit()

        resp = client.put(f"/api/tags/form/{t.id}", headers=auth_headers, json={"name": "新名"})
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "新名"


class TestDeleteTag:
    def test_delete_tag(self, client, db, auth_headers):
        t = Tag(name="保湿", type=TagType.effect)
        db.session.add(t)
        db.session.commit()
        tid = t.id

        resp = client.delete(f"/api/tags/effect/{tid}", headers=auth_headers)
        assert resp.status_code == 200

        assert Tag.query.get(tid) is None
