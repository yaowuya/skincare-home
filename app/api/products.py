import os
from datetime import datetime
from flask import request, g
from flask_restx import Namespace, Resource, fields
from werkzeug.datastructures import FileStorage
from app import db
from app.models.product import Product, ProductImage as ProductImageModel, Tag, TagType
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
        product.tags = [t for t in product.tags if t.type != TagType.form]
        if data["form_tag_ids"]:
            product.tags.extend(
                Tag.query.filter(
                    Tag.id.in_(data["form_tag_ids"]), Tag.type == TagType.form
                ).all()
            )
    if "effect_tag_ids" in data:
        product.tags = [t for t in product.tags if t.type != TagType.effect]
        if data["effect_tag_ids"]:
            product.tags.extend(
                Tag.query.filter(
                    Tag.id.in_(data["effect_tag_ids"]), Tag.type == TagType.effect
                ).all()
            )
    if "function_tag_ids" in data:
        product.tags = [t for t in product.tags if t.type != TagType.function]
        if data["function_tag_ids"]:
            product.tags.extend(
                Tag.query.filter(
                    Tag.id.in_(data["function_tag_ids"]), Tag.type == TagType.function
                ).all()
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
            query = query.filter(
                Product.tags.any(db.and_(Tag.id == form_type_id, Tag.type == TagType.form))
            )

        effect_type_id = request.args.get("effect_type_id")
        if effect_type_id:
            query = query.filter(
                Product.tags.any(db.and_(Tag.id == effect_type_id, Tag.type == TagType.effect))
            )

        function_type_id = request.args.get("function_type_id")
        if function_type_id:
            query = query.filter(
                Product.tags.any(db.and_(Tag.id == function_type_id, Tag.type == TagType.function))
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
            for image in product.images:
                delete_image(image.url)
            if product.image and not product.images:
                delete_image(product.image)
            db.session.delete(product)
            db.session.commit()
            return {"message": "Product deleted"}
        return inner()


@products_ns.route("/<string:id>/image")
class ProductImageResource(Resource):
    @products_ns.doc(security="Bearer")
    @products_ns.expect(upload_parser)
    def post(self, id):
        """上传产品图片"""
        @admin_required
        def inner():
            product = Product.query.get_or_404(id)
            args = upload_parser.parse_args()
            file = args["image"]

            image_url = save_image(file, str(product.id))
            image = ProductImageModel(
                product=product,
                url=image_url,
                sort_order=len(product.images),
            )
            db.session.add(image)
            if not product.image:
                product.image = image_url
            db.session.commit()
            return image.to_dict()
        return inner()

    @products_ns.doc(security="Bearer")
    def delete(self, id):
        """删除产品图片"""
        @admin_required
        def inner():
            product = Product.query.get_or_404(id)
            for image in product.images:
                delete_image(image.url)
            if product.image:
                delete_image(product.image)
            product.images = []
            product.image = ""
            db.session.commit()
            return {"message": "Images deleted"}
        return inner()


@products_ns.route("/<string:id>/images/<string:image_id>")
class ProductSingleImage(Resource):
    @products_ns.doc(security="Bearer")
    def delete(self, id, image_id):
        """删除单张产品图片"""
        @admin_required
        def inner():
            product = Product.query.get_or_404(id)
            image = ProductImageModel.query.filter_by(id=image_id, product_id=product.id).first_or_404()
            delete_image(image.url)
            db.session.delete(image)
            db.session.flush()

            remaining = (
                ProductImageModel.query.filter_by(product_id=product.id)
                .order_by(ProductImageModel.sort_order)
                .all()
            )
            for index, remaining_image in enumerate(remaining):
                remaining_image.sort_order = index
            product.image = remaining[0].url if remaining else ""
            db.session.commit()
            return {"message": "Image deleted"}
        return inner()
