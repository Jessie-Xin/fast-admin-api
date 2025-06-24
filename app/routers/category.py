from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select

from app.core.dependencies import CurrentActiveUser, CurrentAdminUser, SessionDep
from app.models.category import Category
from app.schemas.category import (CategoryCreate, CategoryListResponse,
                                CategoryResponse, CategoryUpdate)

router = APIRouter(prefix="/api/categories", tags=["categories"])


# 获取分类列表
@router.get("/", response_model=CategoryListResponse)
async def get_categories(
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """获取分类列表"""
    categories = session.exec(select(Category).offset(skip).limit(limit)).all()
    total = session.exec(select(Category)).count()
    
    return CategoryListResponse(total=total, categories=categories)


# 获取分类详情
@router.get("/{categoryId}", response_model=CategoryResponse)
async def get_category(
    categoryId: int,
    session: SessionDep
):
    """获取分类详情"""
    category = session.get(Category, categoryId)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    return category


# 创建分类（需要管理员权限）
@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    session: SessionDep,
    current_user: CurrentAdminUser
):
    """创建分类"""
    # 检查分类名是否存在
    db_category = session.exec(
        select(Category).where(Category.name == category_data.name)
    ).first()
    if db_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分类名已存在"
        )
    
    # 创建分类
    new_category = Category(**category_data.model_dump())
    
    session.add(new_category)
    session.commit()
    session.refresh(new_category)
    
    return new_category


# 更新分类（需要管理员权限）
@router.put("/{categoryId}", response_model=CategoryResponse)
async def update_category(
    categoryId: int,
    category_data: CategoryUpdate,
    session: SessionDep,
    current_user: CurrentAdminUser
):
    """更新分类"""
    category = session.get(Category, categoryId)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    # 检查分类名是否存在
    if category_data.name and category_data.name != category.name:
        db_category = session.exec(
            select(Category).where(Category.name == category_data.name)
        ).first()
        if db_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类名已存在"
            )
        category.name = category_data.name
    
    # 更新描述
    if category_data.description is not None:
        category.description = category_data.description
    
    # 更新时间
    category.updated_at = datetime.utcnow()
    
    session.add(category)
    session.commit()
    session.refresh(category)
    
    return category


# 删除分类（需要管理员权限）
@router.delete("/{categoryId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    categoryId: int,
    session: SessionDep,
    current_user: CurrentAdminUser
):
    """删除分类"""
    category = session.get(Category, categoryId)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    session.delete(category)
    session.commit() 