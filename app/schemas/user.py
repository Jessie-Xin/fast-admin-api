from datetime import datetime
from typing import List, Optional, Any

from pydantic import BaseModel, EmailStr, Field


# 基础用户模型
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    is_active: bool = True
    is_admin: bool = False


# 创建用户请求模型
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


# 用户信息响应模型
class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime


# 用户列表响应模型
class UserListResponse(BaseModel):
    total: int
    users: List[UserResponse]


# 用户更新请求模型
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
