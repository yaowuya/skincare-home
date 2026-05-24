from flask import g
from flask_restx import Namespace, Resource, fields
from app import db
from app.models.user import User
from app.auth.decorators import generate_token, jwt_required

auth_ns = Namespace("auth", description="认证管理")

# --- Request/response models ---
register_model = auth_ns.model("Register", {
    "username": fields.String(required=True, description="用户名"),
    "email": fields.String(required=True, description="邮箱"),
    "password": fields.String(required=True, description="密码"),
})

login_model = auth_ns.model("Login", {
    "username": fields.String(required=True, description="用户名"),
    "password": fields.String(required=True, description="密码"),
})

password_model = auth_ns.model("ChangePassword", {
    "old_password": fields.String(required=True),
    "new_password": fields.String(required=True),
})

user_model = auth_ns.model("User", {
    "id": fields.String,
    "username": fields.String,
    "email": fields.String,
    "role": fields.String,
    "is_approved": fields.Boolean,
})

msg_model = auth_ns.model("Message", {
    "message": fields.String,
})


@auth_ns.route("/register")
class Register(Resource):
    @auth_ns.expect(register_model, validate=True)
    @auth_ns.response(201, "Registered", msg_model)
    @auth_ns.response(409, "Username or email exists")
    def post(self):
        """用户注册"""
        data = auth_ns.payload
        if User.query.filter(
            (User.username == data["username"]) | (User.email == data["email"])
        ).first():
            auth_ns.abort(409, "Username or email already exists")
        user = User(
            username=data["username"],
            email=data["email"],
            role="user",
            is_approved=False,
        )
        user.set_password(data["password"])
        db.session.add(user)
        db.session.commit()
        return {"message": "Registration successful, awaiting admin approval"}, 201


@auth_ns.route("/login")
class Login(Resource):
    @auth_ns.expect(login_model, validate=True)
    def post(self):
        """用户登录"""
        data = auth_ns.payload
        user = User.query.filter_by(username=data["username"]).first()
        if not user or not user.check_password(data["password"]):
            auth_ns.abort(401, "Invalid credentials")
        if not user.is_approved:
            auth_ns.abort(403, "Account not approved yet")
        token = generate_token(user.id)
        return {"access_token": token, "user": user.to_dict()}


@auth_ns.route("/me")
class Me(Resource):
    @auth_ns.doc(security="Bearer")
    @auth_ns.marshal_with(user_model)
    def get(self):
        """获取当前用户信息"""
        from app.auth.decorators import jwt_required as jwtr
        @jwtr
        def inner():
            return g.current_user.to_dict()
        return inner()


@auth_ns.route("/password")
class ChangePassword(Resource):
    @auth_ns.expect(password_model, validate=True)
    def put(self):
        """修改密码"""
        from app.auth.decorators import jwt_required as jwtr
        @jwtr
        def inner():
            data = auth_ns.payload
            user = g.current_user
            if not user.check_password(data["old_password"]):
                auth_ns.abort(400, "Old password is incorrect")
            user.set_password(data["new_password"])
            db.session.commit()
            return {"message": "Password updated"}
        return inner()
