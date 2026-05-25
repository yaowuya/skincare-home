import re
from pydantic import BaseModel, field_validator
from app.models.user import RoleEnum


class UserCreateSchema(BaseModel):
    username: str
    email: str
    password: str
    role: RoleEnum = RoleEnum.user
    is_approved: bool = False

    @field_validator("username")
    @classmethod
    def username_not_blank(cls, v):
        if not v.strip():
            raise ValueError("用户名不能为空")
        return v

    @field_validator("email")
    @classmethod
    def email_format(cls, v):
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("邮箱格式不正确")
        return v

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 4:
            raise ValueError("密码长度至少4位")
        return v


class UserUpdateSchema(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None
    role: RoleEnum | None = None

    @field_validator("username")
    @classmethod
    def username_not_blank(cls, v):
        if v is not None and not v.strip():
            raise ValueError("用户名不能为空")
        return v

    @field_validator("email")
    @classmethod
    def email_format(cls, v):
        if v is not None and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("邮箱格式不正确")
        return v


class ApproveSchema(BaseModel):
    approved: bool
