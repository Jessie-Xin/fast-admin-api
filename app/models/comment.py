from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Comment(SQLModel, table=True):
    """评论模型"""
    __tablename__ = "comment"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 外键
    author_id: int = Field(foreign_key="user.id")
    post_id: int = Field(foreign_key="post.id")
    
    # 关联关系
    author: "User" = Relationship(back_populates="comments")
    post: "Post" = Relationship(back_populates="comments") 