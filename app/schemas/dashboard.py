from typing import List

from pydantic import BaseModel

from app.schemas.comment import CommentResponse
from app.schemas.post import PostBrief


# 仪表盘摘要响应模型
class DashboardSummary(BaseModel):
    total_posts: int
    total_categories: int
    total_tags: int
    total_comments: int
    total_users: int
    recent_posts: List[PostBrief]
    recent_comments: List[CommentResponse]
