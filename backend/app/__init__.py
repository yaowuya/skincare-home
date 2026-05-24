import os
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restx import Api

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_object=None):
    app = Flask(__name__, static_folder="../static", static_url_path="")

    if config_object:
        app.config.from_object(config_object)
    else:
        from config import Config
        app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Ensure upload directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Flask-RESTx API
    api = Api(
        app,
        doc="/api/docs/",
        prefix="/api",
        title="Skincare Product API",
        description="化妆品产品管理平台 API",
        default="auth",
        default_label="认证相关",
    )

    # Register namespaces
    from app.api.auth import auth_ns
    from app.api.users import users_ns
    from app.api.products import products_ns
    from app.api.tags import tags_ns

    api.add_namespace(auth_ns, path="/auth")
    api.add_namespace(users_ns, path="/users")
    api.add_namespace(products_ns, path="/products")
    api.add_namespace(tags_ns, path="/tags")

    # SPA fallback: serve Vue frontend for non-API routes
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static")

    @app.route("/")
    def index():
        return send_from_directory(static_dir, "index.html")

    @app.route("/assets/<path:filename>")
    def serve_assets(filename):
        return send_from_directory(os.path.join(static_dir, "assets"), filename)

    @app.route("/uploads/<path:filename>")
    def serve_uploads(filename):
        upload_dir = app.config["UPLOAD_FOLDER"]
        return send_from_directory(upload_dir, filename)

    @app.route("/<path:path>")
    def serve_spa(path):
        if path.startswith("api/") or path.startswith("uploads/"):
            from flask import jsonify
            return jsonify({"message": "Not Found"}), 404
        return send_from_directory(static_dir, "index.html")

    # Register CLI commands
    from app.cli import register_commands
    register_commands(app)

    return app
