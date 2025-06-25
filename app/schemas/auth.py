from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class Token(BaseModel):
    """访问令牌"""

    access_token: str
    token_type: str
    user_id: int = None
    username: str = None
    is_admin: bool = False


class TokenData(BaseModel):
    """令牌数据"""

    sub: str = None


class LoginRequest(BaseModel):
    """登录请求"""

    username: str = Field(..., min_length=1, description="用户名或邮箱")
    password: str = Field(..., min_length=1, description="密码")

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("用户名不能为空")
        return v

    @field_validator("password")
    @classmethod
    def password_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("密码不能为空")
        return v


class RegisterResponse(BaseModel):
    """注册成功响应"""

    user_id: int
    username: str
    email: str
    access_token: str
    token_type: str = "bearer"
    created_at: datetime


class PasswordResetRequest(BaseModel):
    """密码重置请求"""

    email: EmailStr


class PasswordReset(BaseModel):
    """密码重置"""

    token: str
    new_password: str


class PasswordChange(BaseModel):
    """密码修改"""

    current_password: str
    new_password: str
