import uuid
from datetime import datetime, timezone
from app import db


# --- Association tables ---

product_form_tag = db.Table(
    "product_form_tags",
    db.Column("product_id", db.String(36), db.ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    db.Column("form_type_id", db.String(36), db.ForeignKey("form_types.id", ondelete="CASCADE"), primary_key=True),
)

product_effect_tag = db.Table(
    "product_effect_tags",
    db.Column("product_id", db.String(36), db.ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    db.Column("effect_type_id", db.String(36), db.ForeignKey("effect_types.id", ondelete="CASCADE"), primary_key=True),
)

product_function_tag = db.Table(
    "product_function_tags",
    db.Column("product_id", db.String(36), db.ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    db.Column("function_type_id", db.String(36), db.ForeignKey("function_types.id", ondelete="CASCADE"), primary_key=True),
)


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    ingredients = db.Column(db.Text, default="")
    image = db.Column(db.String(300), default="")
    published_at = db.Column(db.Date, nullable=True)
    created_by = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # relationships
    form_tags = db.relationship("FormType", secondary=product_form_tag, lazy="selectin")
    effect_tags = db.relationship("EffectType", secondary=product_effect_tag, lazy="selectin")
    function_tags = db.relationship("FunctionType", secondary=product_function_tag, lazy="selectin")

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "ingredients": self.ingredients,
            "image": self.image,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "form_tags": [t.to_dict() for t in (self.form_tags or [])],
            "effect_tags": [t.to_dict() for t in (self.effect_tags or [])],
            "function_tags": [t.to_dict() for t in (self.function_tags or [])],
            "created_by": str(self.created_by) if self.created_by else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class FormType(db.Model):
    __tablename__ = "form_types"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), unique=True, nullable=False)

    def to_dict(self):
        return {"id": str(self.id), "name": self.name}


class EffectType(db.Model):
    __tablename__ = "effect_types"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), unique=True, nullable=False)

    def to_dict(self):
        return {"id": str(self.id), "name": self.name}


class FunctionType(db.Model):
    __tablename__ = "function_types"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), unique=True, nullable=False)

    def to_dict(self):
        return {"id": str(self.id), "name": self.name}
