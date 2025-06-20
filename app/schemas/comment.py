from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.user import UserResponse


# 基础评论模型
class CommentBase(BaseModel):
    content: str = Field(..., min_length=1)


# 创建评论请求模型
class CommentCreate(CommentBase):
    post_id: int


# 评论响应模型
class CommentResponse(CommentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    author: UserResponse
    post_id: int


# 评论列表响应模型
class CommentListResponse(BaseModel):
    total: int
    comments: List[CommentResponse]


# 评论更新请求模型
class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1) 