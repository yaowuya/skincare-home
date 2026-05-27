import os
from datetime import timedelta
from dotenv import load_dotenv

# Load .env from project root
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:root@localhost:5432/skincare",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    _project_root = os.path.dirname(os.path.abspath(__file__))
    _raw_upload_folder = os.environ.get("UPLOAD_FOLDER", "uploads")
    if os.path.isabs(_raw_upload_folder):
        UPLOAD_FOLDER = _raw_upload_folder
    else:
        UPLOAD_FOLDER = os.path.abspath(os.path.join(_project_root, _raw_upload_folder))
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024))  # 5MB

    JWT_SECRET = os.environ.get("JWT_SECRET", SECRET_KEY)
    JWT_EXPIRATION_HOURS = int(os.environ.get("JWT_EXPIRATION_HOURS", 24))

    JSON_AS_ASCII = False  # support Chinese in JSON responses


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    UPLOAD_FOLDER = "/tmp/test-uploads"
    JWT_SECRET = "test-secret"
    JWT_EXPIRATION_HOURS = 24
