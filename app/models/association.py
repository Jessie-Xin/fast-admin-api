from sqlmodel import Field, SQLModel


class PostTagLink(SQLModel, table=True):
    """文章与标签多对多关联表"""
    __tablename__ = "post_tag_link"
    
    post_id: int = Field(foreign_key="post.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True) 