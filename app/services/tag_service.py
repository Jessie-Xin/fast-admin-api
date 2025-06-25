from sqlmodel import Session, select
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate

# 获取标签列表业务逻辑
def get_tags_service(session: Session, skip: int = 0, limit: int = 100):
    """获取标签列表业务逻辑"""
    tags = session.exec(select(Tag).offset(skip).limit(limit)).all()
    total = len(session.exec(select(Tag)).all())
    return total, tags

# 获取标签详情业务逻辑
def get_tag_service(tagId: int, session: Session):
    """获取标签详情业务逻辑"""
    return session.get(Tag, tagId)

# 检查标签名是否存在
def check_tag_exists(session: Session, name: str):
    """检查标签名是否存在"""
    db_tag = session.exec(select(Tag).where(Tag.name == name)).first()
    return db_tag is not None

# 创建标签业务逻辑
def create_tag_service(tag_data: TagCreate, session: Session):
    """创建标签业务逻辑"""
    new_tag = Tag(**tag_data.model_dump())
    session.add(new_tag)
    session.commit()
    session.refresh(new_tag)
    return new_tag

# 更新标签业务逻辑
def update_tag_service(tag: Tag, tag_data: TagUpdate, session: Session):
    """更新标签业务逻辑"""
    if tag_data.name != tag.name:
        tag.name = tag_data.name
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag

# 删除标签业务逻辑
def delete_tag_service(tag: Tag, session: Session):
    """删除标签业务逻辑"""
    session.delete(tag)
    session.commit() 