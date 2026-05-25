from flask_restx import Namespace, Resource, fields
from pydantic import ValidationError
from app import db
from app.models.user import User, RoleEnum
from app.auth.decorators import admin_required
from app.api.schemas import UserCreateSchema, UserUpdateSchema, ApproveSchema

users_ns = Namespace("users", description="用户管理（管理员）")

user_model = users_ns.model("User", {
    "username": fields.String(required=True),
    "email": fields.String(required=True),
    "password": fields.String(required=False, description="留空则不修改"),
    "role": fields.String(default="user", enum=["admin", "user"]),
    "is_approved": fields.Boolean(default=False),
})

approve_model = users_ns.model("Approve", {
    "approved": fields.Boolean(required=True),
})


@users_ns.route("/")
class UserList(Resource):
    @users_ns.doc(security="Bearer")
    def get(self):
        """获取用户列表"""
        @admin_required
        def inner():
            from flask import request
            approved = request.args.get("approved")
            query = User.query.order_by(User.created_at.desc())
            if approved is not None:
                query = query.filter_by(is_approved=approved.lower() == "true")
            return [u.to_dict() for u in query.all()]
        return inner()

    @users_ns.doc(security="Bearer")
    @users_ns.expect(user_model, validate=True)
    def post(self):
        """创建用户（管理员）"""
        @admin_required
        def inner():
            data = users_ns.payload
            try:
                schema = UserCreateSchema(**data)
            except ValidationError as e:
                users_ns.abort(400, e.errors())
            if User.query.filter(
                (User.username == schema.username) | (User.email == schema.email)
            ).first():
                users_ns.abort(409, "Username or email already exists")
            user = User(
                username=schema.username,
                email=schema.email,
                role=schema.role,
                is_approved=schema.is_approved,
            )
            user.set_password(schema.password)
            db.session.add(user)
            db.session.commit()
            return user.to_dict(), 201
        return inner()


@users_ns.route("/<string:id>")
class UserDetail(Resource):
    @users_ns.doc(security="Bearer")
    def put(self, id):
        """编辑用户"""
        @admin_required
        def inner():
            user = User.query.get_or_404(id)
            data = users_ns.payload
            try:
                schema = UserUpdateSchema(**data)
            except ValidationError as e:
                users_ns.abort(400, e.errors())
            if schema.username is not None:
                user.username = schema.username
            if schema.email is not None:
                user.email = schema.email
            if schema.role is not None:
                user.role = schema.role
            if schema.password is not None and schema.password:
                user.set_password(schema.password)
            db.session.commit()
            return user.to_dict()
        return inner()

    @users_ns.doc(security="Bearer")
    def delete(self, id):
        """删除用户"""
        @admin_required
        def inner():
            user = User.query.get_or_404(id)
            db.session.delete(user)
            db.session.commit()
            return {"message": "User deleted"}
        return inner()


@users_ns.route("/<string:id>/approve")
class UserApprove(Resource):
    @users_ns.doc(security="Bearer")
    @users_ns.expect(approve_model, validate=True)
    def post(self, id):
        """审核用户"""
        @admin_required
        def inner():
            user = User.query.get_or_404(id)
            data = users_ns.payload
            try:
                schema = ApproveSchema(**data)
            except ValidationError as e:
                users_ns.abort(400, e.errors())
            user.is_approved = schema.approved
            db.session.commit()
            return user.to_dict()
        return inner()
