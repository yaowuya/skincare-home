from flask_restx import Namespace, Resource, fields
from app import db
from app.models.product import FormType, EffectType, FunctionType
from app.auth.decorators import admin_required

tags_ns = Namespace("tags", description="标签管理")

tag_model = tags_ns.model("Tag", {
    "name": fields.String(required=True),
})

TYPE_MAP = {
    "form": (FormType, "form_types"),
    "effect": (EffectType, "effect_types"),
    "function": (FunctionType, "function_types"),
}


def get_model(tag_type):
    model_cls, _ = TYPE_MAP.get(tag_type, (None, None))
    if not model_cls:
        tags_ns.abort(400, f"Invalid type: {tag_type}. Use form/effect/function")
    return model_cls


@tags_ns.route("/<string:tag_type>")
class TagList(Resource):
    def get(self, tag_type):
        """获取标签列表（公开）"""
        model_cls = get_model(tag_type)
        return [t.to_dict() for t in model_cls.query.order_by(model_cls.name).all()]

    @tags_ns.doc(security="Bearer")
    @tags_ns.expect(tag_model, validate=True)
    def post(self, tag_type):
        """创建标签（管理员）"""
        @admin_required
        def inner():
            model_cls = get_model(tag_type)
            name = tags_ns.payload["name"].strip()
            if not name:
                tags_ns.abort(400, "Tag name cannot be empty")
            if model_cls.query.filter_by(name=name).first():
                tags_ns.abort(409, f"Tag '{name}' already exists")
            tag = model_cls(name=name)
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
            model_cls = get_model(tag_type)
            tag = model_cls.query.get_or_404(id)
            name = tags_ns.payload["name"].strip()
            if not name:
                tags_ns.abort(400, "Tag name cannot be empty")
            existing = model_cls.query.filter(
                model_cls.name == name, model_cls.id != id
            ).first()
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
            model_cls = get_model(tag_type)
            tag = model_cls.query.get_or_404(id)
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted"}
        return inner()
