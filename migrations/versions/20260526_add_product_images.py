"""add product images

Revision ID: 20260526_product_images
Revises: 00399257896b
Create Date: 2026-05-26 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "20260526_product_images"
down_revision = "00399257896b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "product_images",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("url", sa.String(length=300), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("product_images", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_product_images_product_id"), ["product_id"], unique=False)

    op.execute(
        """
        INSERT INTO product_images (id, product_id, url, sort_order, created_at)
        SELECT id, id, image, 0, created_at
        FROM products
        WHERE image IS NOT NULL AND image != ''
        """
    )


def downgrade():
    with op.batch_alter_table("product_images", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_product_images_product_id"))
    op.drop_table("product_images")
