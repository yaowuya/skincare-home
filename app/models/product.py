import enum
import uuid
from datetime import datetime, timezone
from app import db


class TagType(str, enum.Enum):
    form = "form"
    effect = "effect"
    function = "function"


# --- Association table ---

product_tags = db.Table(
    "product_tags",
    db.Column("product_id", db.String(36), db.ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    db.Column("tag_id", db.String(36), db.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.Enum(TagType), nullable=False)

    __table_args__ = (db.UniqueConstraint("name", "type", name="uq_tag_name_type"),)

    def to_dict(self):
        return {"id": str(self.id), "name": self.name}


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
    tags = db.relationship("Tag", secondary=product_tags, lazy="selectin")

    def to_dict(self):
        form_tags = [t.to_dict() for t in self.tags if t.type == TagType.form]
        effect_tags = [t.to_dict() for t in self.tags if t.type == TagType.effect]
        function_tags = [t.to_dict() for t in self.tags if t.type == TagType.function]
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "ingredients": self.ingredients,
            "image": self.image,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "form_tags": form_tags,
            "effect_tags": effect_tags,
            "function_tags": function_tags,
            "created_by": str(self.created_by) if self.created_by else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
