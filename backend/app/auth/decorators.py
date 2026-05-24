import jwt
import datetime
from functools import wraps
from flask import request, g, current_app
from app.models.user import User


def generate_token(user_id, secret=None, expiration_hours=None):
    secret = secret or current_app.config["JWT_SECRET"]
    hours = expiration_hours or current_app.config["JWT_EXPIRATION_HOURS"]
    payload = {
        "user_id": str(user_id),
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=hours),
        "iat": datetime.datetime.now(datetime.timezone.utc),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_token(token, secret=None):
    secret = secret or current_app.config["JWT_SECRET"]
    return jwt.decode(token, secret, algorithms=["HS256"])


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            from flask_restx import abort
            abort(401, message="Missing or invalid Authorization header")
        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
            user = User.query.get(payload["user_id"])
            if not user:
                from flask_restx import abort
                abort(401, message="User not found")
            g.current_user = user
        except jwt.ExpiredSignatureError:
            from flask_restx import abort
            abort(401, message="Token expired")
        except jwt.InvalidTokenError:
            from flask_restx import abort
            abort(401, message="Invalid token")
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    @jwt_required
    def decorated(*args, **kwargs):
        if g.current_user.role != "admin":
            from flask_restx import abort
            abort(403, message="Admin access required")
        return f(*args, **kwargs)
    return decorated
