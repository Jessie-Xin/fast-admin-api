from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


# 基础标签模型
class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=30)


# 创建标签请求模型
class TagCreate(TagBase):
    pass


# 标签响应模型
class TagResponse(TagBase):
    id: int
    created_at: datetime


# 标签列表响应模型
class TagListResponse(BaseModel):
    total: int
    tags: List[TagResponse]


# 标签更新请求模型
class TagUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=30)
