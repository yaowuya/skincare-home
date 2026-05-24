import io
import os
import pytest
from werkzeug.datastructures import FileStorage
from app import db as _db
from app.models.product import Product
from app.utils.upload import allowed_file, save_image, delete_image


def _make_filestorage(content=b"fake-png-content", filename="test_image.png"):
    """Helper to create a Werkzeug FileStorage from bytes."""
    stream = io.BytesIO(content)
    return FileStorage(stream=stream, filename=filename)


class TestAllowedFile:
    def test_allowed_jpg(self):
        assert allowed_file("photo.jpg") is True

    def test_allowed_png(self):
        assert allowed_file("photo.png") is True

    def test_allowed_webp(self):
        assert allowed_file("photo.webp") is True

    def test_disallowed_pdf(self):
        assert allowed_file("doc.pdf") is False

    def test_no_extension(self):
        assert allowed_file("photo") is False

    def test_no_filename(self):
        assert allowed_file("") is False


class TestSaveAndDeleteImage:
    def test_save_image_raises_on_invalid_type(self, app, db):
        with app.app_context():
            file = _make_filestorage(filename="test.pdf")
            with pytest.raises(ValueError, match="File type not allowed"):
                save_image(file, "product-1")

    def test_save_and_delete_image(self, app, db):
        from flask import current_app
        with app.app_context():
            # Ensure upload dir exists
            os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)

            product = Product(name="Test")
            db.session.add(product)
            db.session.commit()

            file = _make_filestorage()

            path = save_image(file, str(product.id))
            assert path.startswith("/uploads/")
            assert path.endswith(".png")

            full_path = os.path.join(current_app.config["UPLOAD_FOLDER"], path.lstrip("/uploads/"))
            assert os.path.exists(full_path)

            # Delete and verify
            delete_image(path)
            assert not os.path.exists(full_path)

    def test_delete_empty_path(self, app, db):
        delete_image("")  # should not raise
        delete_image(None)  # should not raise
