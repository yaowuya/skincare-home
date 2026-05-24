import os
from datetime import datetime
from flask import request, g
from flask_restx import Namespace, Resource, fields
from werkzeug.datastructures import FileStorage
from app import db
from app.models.product import Product, FormType, EffectType, FunctionType
from app.auth.decorators import admin_required
from app.utils.upload import save_image, delete_image


def _parse_date(date_str):
    """Convert ISO date string to date object, or return None."""
    if not date_str:
        return None
    try:
        return datetime.strptime(str(date_str), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


products_ns = Namespace("products", description="产品管理")

# --- Request models ---
product_model = products_ns.model("Product", {
    "name": fields.String(required=True),
    "description": fields.String(default=""),
    "ingredients": fields.String(default=""),
    "published_at": fields.String(description="ISO date string, e.g. 2024-03-15"),
    "form_tag_ids": fields.List(fields.String, description="剂型标签 ID 列表"),
    "effect_tag_ids": fields.List(fields.String, description="功效标签 ID 列表"),
    "function_tag_ids": fields.List(fields.String, description="功能标签 ID 列表"),
})

upload_parser = products_ns.parser()
upload_parser.add_argument(
    "image", location="files", type=FileStorage, required=True, help="产品图片"
)


def apply_tag_ids(product, data):
    """Helper to set tag relationships from ID lists."""
    if "form_tag_ids" in data:
        product.form_tags = (
            FormType.query.filter(FormType.id.in_(data["form_tag_ids"])).all()
            if data["form_tag_ids"]
            else []
        )
    if "effect_tag_ids" in data:
        product.effect_tags = (
            EffectType.query.filter(EffectType.id.in_(data["effect_tag_ids"])).all()
            if data["effect_tag_ids"]
            else []
        )
    if "function_tag_ids" in data:
        product.function_tags = (
            FunctionType.query.filter(FunctionType.id.in_(data["function_tag_ids"])).all()
            if data["function_tag_ids"]
            else []
        )


@products_ns.route("/")
class ProductList(Resource):
    def get(self):
        """产品列表（公开），支持搜索、分页、筛选"""
        query = Product.query

        # Search
        search = request.args.get("search", "").strip()
        if search:
            like = f"%{search}%"
            query = query.filter(
                db.or_(
                    Product.name.ilike(like),
                    Product.description.ilike(like),
                    Product.ingredients.ilike(like),
                )
            )

        # Filter by tag
        form_type_id = request.args.get("form_type_id")
        if form_type_id:
            query = query.filter(Product.form_tags.any(FormType.id == form_type_id))

        effect_type_id = request.args.get("effect_type_id")
        if effect_type_id:
            query = query.filter(Product.effect_tags.any(EffectType.id == effect_type_id))

        function_type_id = request.args.get("function_type_id")
        if function_type_id:
            query = query.filter(
                Product.function_tags.any(FunctionType.id == function_type_id)
            )

        # Sort
        sort_by = request.args.get("sort_by", "published_at")
        sort_order = request.args.get("sort_order", "desc")
        sort_col = getattr(Product, sort_by, Product.published_at)
        if sort_order == "asc":
            query = query.order_by(sort_col.asc())
        else:
            query = query.order_by(sort_col.desc())

        # Pagination
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "items": [p.to_dict() for p in pagination.items],
            "total": pagination.total,
            "page": page,
            "per_page": per_page,
            "pages": pagination.pages,
        }

    @products_ns.doc(security="Bearer")
    @products_ns.expect(product_model, validate=True)
    def post(self):
        """创建产品（管理员）"""
        @admin_required
        def inner():
            data = products_ns.payload
            product = Product(
                name=data["name"],
                description=data.get("description", ""),
                ingredients=data.get("ingredients", ""),
                published_at=_parse_date(data.get("published_at")),
                created_by=g.current_user.id,
            )
            apply_tag_ids(product, data)
            db.session.add(product)
            db.session.commit()
            return product.to_dict(), 201
        return inner()


@products_ns.route("/<string:id>")
class ProductDetail(Resource):
    def get(self, id):
        """产品详情（公开）"""
        product = Product.query.get_or_404(id)
        return product.to_dict()

    @products_ns.doc(security="Bearer")
    @products_ns.expect(product_model)
    def put(self, id):
        """编辑产品（管理员）"""
        @admin_required
        def inner():
            product = Product.query.get_or_404(id)
            data = products_ns.payload
            if "name" in data:
                product.name = data["name"]
            if "description" in data:
                product.description = data["description"]
            if "ingredients" in data:
                product.ingredients = data["ingredients"]
            if "published_at" in data:
                product.published_at = _parse_date(data["published_at"])
            apply_tag_ids(product, data)
            db.session.commit()
            return product.to_dict()
        return inner()

    @products_ns.doc(security="Bearer")
    def delete(self, id):
        """删除产品（管理员）"""
        @admin_required
        def inner():
            product = Product.query.get_or_404(id)
            delete_image(product.image)
            db.session.delete(product)
            db.session.commit()
            return {"message": "Product deleted"}
        return inner()


@products_ns.route("/<string:id>/image")
class ProductImage(Resource):
    @products_ns.doc(security="Bearer")
    @products_ns.expect(upload_parser)
    def post(self, id):
        """上传产品图片"""
        @admin_required
        def inner():
            product = Product.query.get_or_404(id)
            args = upload_parser.parse_args()
            file = args["image"]

            # Delete old image if exists
            if product.image:
                delete_image(product.image)

            image_url = save_image(file, str(product.id))
            product.image = image_url
            db.session.commit()
            return {"image": image_url}
        return inner()

    @products_ns.doc(security="Bearer")
    def delete(self, id):
        """删除产品图片"""
        @admin_required
        def inner():
            product = Product.query.get_or_404(id)
            if product.image:
                delete_image(product.image)
                product.image = ""
                db.session.commit()
            return {"message": "Image deleted"}
        return inner()
