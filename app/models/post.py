from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.association import PostTagLink

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.category import Category
    from app.models.tag import Tag
    from app.models.comment import Comment


class Post(SQLModel, table=True):
    """文章模型"""
    __tablename__ = "post"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    content_markdown: str
    content_html: str
    summary: Optional[str] = None
    published: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 外键
    author_id: int = Field(foreign_key="user.id")
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    
    # 关联关系
    author: "User" = Relationship(back_populates="posts")
    category: Optional["Category"] = Relationship(back_populates="posts")
    tags: List["Tag"] = Relationship(back_populates="posts", link_model=PostTagLink)
    comments: List["Comment"] = Relationship(back_populates="post") 