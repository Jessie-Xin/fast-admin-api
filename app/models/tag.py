from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.association import PostTagLink


class Tag(SQLModel, table=True):
    """标签模型"""
    __tablename__ = "tag"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 关联关系
    posts: List["Post"] = Relationship(back_populates="tags", link_model=PostTagLink) 