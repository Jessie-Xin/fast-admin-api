from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Category(SQLModel, table=True):
    """分类模型"""
    __tablename__ = "category"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 关联关系
    posts: List["Post"] = Relationship(back_populates="category") 