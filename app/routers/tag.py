from typing import List

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select

from app.core.dependencies import CurrentActiveUser, CurrentAdminUser, SessionDep
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagListResponse, TagResponse, TagUpdate

router = APIRouter(prefix="/api/tags", tags=["tags"])


# 获取标签列表
@router.get("/", response_model=TagListResponse)
async def get_tags(
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """获取标签列表"""
    tags = session.exec(select(Tag).offset(skip).limit(limit)).all()
    total = session.exec(select(Tag)).count()
    
    return TagListResponse(total=total, tags=tags)


# 获取标签详情
@router.get("/{tagId}", response_model=TagResponse)
async def get_tag(
    tagId: int,
    session: SessionDep
):
    """获取标签详情"""
    tag = session.get(Tag, tagId)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    
    return tag


# 创建标签（需要管理员权限）
@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    session: SessionDep,
    current_user: CurrentAdminUser
):
    """创建标签"""
    # 检查标签名是否存在
    db_tag = session.exec(
        select(Tag).where(Tag.name == tag_data.name)
    ).first()
    if db_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="标签名已存在"
        )
    
    # 创建标签
    new_tag = Tag(**tag_data.model_dump())
    
    session.add(new_tag)
    session.commit()
    session.refresh(new_tag)
    
    return new_tag


# 更新标签（需要管理员权限）
@router.put("/{tagId}", response_model=TagResponse)
async def update_tag(
    tagId: int,
    tag_data: TagUpdate,
    session: SessionDep,
    current_user: CurrentAdminUser
):
    """更新标签"""
    tag = session.get(Tag, tagId)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    
    # 检查标签名是否存在
    if tag_data.name != tag.name:
        db_tag = session.exec(
            select(Tag).where(Tag.name == tag_data.name)
        ).first()
        if db_tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="标签名已存在"
            )
        tag.name = tag_data.name
    
    session.add(tag)
    session.commit()
    session.refresh(tag)
    
    return tag


# 删除标签（需要管理员权限）
@router.delete("/{tagId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tagId: int,
    session: SessionDep,
    current_user: CurrentAdminUser
):
    """删除标签"""
    tag = session.get(Tag, tagId)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    
    session.delete(tag)
    session.commit() 