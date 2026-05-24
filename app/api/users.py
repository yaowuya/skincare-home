from flask_restx import Namespace, Resource, fields
from app import db
from app.models.user import User
from app.auth.decorators import admin_required

users_ns = Namespace("users", description="用户管理（管理员）")

user_model = users_ns.model("User", {
    "username": fields.String(required=True),
    "email": fields.String(required=True),
    "password": fields.String(required=False, description="留空则不修改"),
    "role": fields.String(default="user"),
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
            if User.query.filter(
                (User.username == data["username"]) | (User.email == data["email"])
            ).first():
                users_ns.abort(409, "Username or email already exists")
            user = User(
                username=data["username"],
                email=data["email"],
                role=data.get("role", "user"),
                is_approved=data.get("is_approved", False),
            )
            user.set_password(data["password"])
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
            if "username" in data:
                user.username = data["username"]
            if "email" in data:
                user.email = data["email"]
            if "role" in data:
                user.role = data["role"]
            if "password" in data and data["password"]:
                user.set_password(data["password"])
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
            user.is_approved = users_ns.payload["approved"]
            db.session.commit()
            return user.to_dict()
        return inner()
