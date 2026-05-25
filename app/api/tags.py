from flask_restx import Namespace, Resource, fields
from app import db
from app.models.product import Tag, TagType
from app.auth.decorators import admin_required

tags_ns = Namespace("tags", description="标签管理")

tag_model = tags_ns.model("Tag", {
    "name": fields.String(required=True),
})


def get_tag_type(tag_type_str):
    try:
        return TagType(tag_type_str)
    except ValueError:
        tags_ns.abort(400, f"Invalid type: {tag_type_str}. Use form/effect/function")


@tags_ns.route("/<string:tag_type>")
class TagList(Resource):
    def get(self, tag_type):
        """获取标签列表（公开）"""
        t = get_tag_type(tag_type)
        return [t.to_dict() for t in Tag.query.filter(Tag.type == t).order_by(Tag.name).all()]

    @tags_ns.doc(security="Bearer")
    @tags_ns.expect(tag_model, validate=True)
    def post(self, tag_type):
        """创建标签（管理员）"""
        @admin_required
        def inner():
            t = get_tag_type(tag_type)
            name = tags_ns.payload["name"].strip()
            if not name:
                tags_ns.abort(400, "Tag name cannot be empty")
            if Tag.query.filter_by(name=name, type=t).first():
                tags_ns.abort(409, f"Tag '{name}' already exists")
            tag = Tag(name=name, type=t)
            db.session.add(tag)
            db.session.commit()
            return tag.to_dict(), 201
        return inner()


@tags_ns.route("/<string:tag_type>/<string:id>")
class TagDetail(Resource):
    @tags_ns.doc(security="Bearer")
    @tags_ns.expect(tag_model, validate=True)
    def put(self, tag_type, id):
        """编辑标签（管理员）"""
        @admin_required
        def inner():
            t = get_tag_type(tag_type)
            tag = Tag.query.filter(Tag.id == id, Tag.type == t).first_or_404()
            name = tags_ns.payload["name"].strip()
            if not name:
                tags_ns.abort(400, "Tag name cannot be empty")
            existing = Tag.query.filter(Tag.name == name, Tag.type == t, Tag.id != id).first()
            if existing:
                tags_ns.abort(409, f"Tag '{name}' already exists")
            tag.name = name
            db.session.commit()
            return tag.to_dict()
        return inner()

    @tags_ns.doc(security="Bearer")
    def delete(self, tag_type, id):
        """删除标签（管理员）"""
        @admin_required
        def inner():
            t = get_tag_type(tag_type)
            tag = Tag.query.filter(Tag.id == id, Tag.type == t).first_or_404()
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted"}
        return inner()
