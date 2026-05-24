import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(file, product_id):
    """Save uploaded image and return the URL path. Removes old image if it exists."""
    if not allowed_file(file.filename):
        raise ValueError("File type not allowed. Supported: jpg, png, webp")

    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{product_id}_{uuid.uuid4().hex[:8]}.{ext}"
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    filepath = os.path.join(upload_dir, unique_name)
    file.save(filepath)
    return f"/uploads/{unique_name}"


def delete_image(image_path):
    """Delete an image file from disk. image_path is like '/uploads/xxx.jpg'."""
    if not image_path:
        return
    filename = image_path.lstrip("/uploads/")
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    filepath = os.path.join(upload_dir, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
