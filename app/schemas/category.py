from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# 基础分类模型
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None


# 创建分类请求模型
class CategoryCreate(CategoryBase):
    pass


# 分类响应模型
class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime


# 分类列表响应模型
class CategoryListResponse(BaseModel):
    total: int
    categories: List[CategoryResponse]


# 分类更新请求模型
class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None 