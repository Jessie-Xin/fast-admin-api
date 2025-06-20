from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.category import CategoryResponse
from app.schemas.tag import TagResponse
from app.schemas.user import UserResponse


# 基础文章模型
class PostBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    content_markdown: str
    summary: Optional[str] = None
    published: bool = False


# 创建文章请求模型
class PostCreate(PostBase):
    category_id: Optional[int] = None
    tag_ids: List[int] = []


# 文章简要响应模型（列表中使用）
class PostBrief(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    published: bool
    created_at: datetime
    updated_at: datetime
    author_id: int


# 文章详细响应模型
class PostResponse(PostBase):
    id: int
    content_html: str
    created_at: datetime
    updated_at: datetime
    author: UserResponse
    category: Optional[CategoryResponse] = None
    tags: List[TagResponse] = []


# 文章列表响应模型
class PostListResponse(BaseModel):
    total: int
    posts: List[PostBrief]


# 文章更新请求模型
class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content_markdown: Optional[str] = None
    summary: Optional[str] = None
    published: Optional[bool] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None 