import click
from flask import current_app
from app import db
from app.models.user import User, RoleEnum
from app.models.product import Tag, TagType


def register_commands(app):
    @app.cli.command("create-admin")
    @click.option("--username", prompt=True, help="Admin username")
    @click.option("--email", prompt=True, help="Admin email")
    @click.password_option(help="Admin password")
    def create_admin(username, email, password):
        """Create the initial admin user (idempotent)."""
        existing = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing:
            if existing.role == RoleEnum.admin:
                click.echo(f"Admin '{username}' already exists.")
                return
            existing.role = RoleEnum.admin
            existing.is_approved = True
            click.echo(f"User '{username}' upgraded to admin.")
        else:
            user = User(
                username=username,
                email=email,
                role=RoleEnum.admin,
                is_approved=True,
            )
            user.set_password(password)
            db.session.add(user)
            click.echo(f"Admin '{username}' created.")
        db.session.commit()

    @app.cli.command("seed-tags")
    def seed_tags():
        """Seed default tags for all three types."""
        seeds = {
            TagType.form: ["防晒", "洁面", "爽肤水", "精华液", "面霜", "眼霜", "面膜", "身体乳", "护手霜"],
            TagType.effect: ["保湿", "美白", "修护", "抗衰", "祛痘", "控油"],
            TagType.function: [
                "问题性肌肤修复", "轻医美护肤", "功效猛药/药妆类",
                "院线套装", "电商爆款", "婴童护肤", "底妆彩妆类",
            ],
        }
        for tag_type, names in seeds.items():
            existing = {t.name for t in Tag.query.filter(Tag.type == tag_type).all()}
            for name in names:
                if name not in existing:
                    db.session.add(Tag(name=name, type=tag_type))
        db.session.commit()
        click.echo("Default tags seeded for form, effect, and function types.")
