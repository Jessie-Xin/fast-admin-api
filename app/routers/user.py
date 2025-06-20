from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.core.dependencies import (CurrentActiveUser, CurrentAdminUser, CurrentUser,
                                 SessionDep)
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserListResponse, UserResponse, UserUpdate

router = APIRouter(prefix="/api/users", tags=["users"])


# 获取当前用户信息
@router.get("/me", response_model=UserResponse)
async def get_user_me(current_user: CurrentUser):
    """获取当前登录用户信息"""
    return current_user


# 更新当前用户信息
@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_data: UserUpdate,
    current_user: CurrentActiveUser,
    session: SessionDep
):
    """更新当前用户信息"""
    # 用户名检查
    if user_data.username and user_data.username != current_user.username:
        db_user = session.exec(
            select(User).where(User.username == user_data.username)
        ).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        current_user.username = user_data.username
    
    # 邮箱检查
    if user_data.email and user_data.email != current_user.email:
        db_user = session.exec(
            select(User).where(User.email == user_data.email)
        ).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
        current_user.email = user_data.email
    
    # 密码更新
    if user_data.password:
        current_user.hashed_password = get_password_hash(user_data.password)
    
    # 更新时间
    current_user.updated_at = datetime.utcnow()
    
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    
    return current_user


# 管理员获取所有用户列表
@router.get("/", response_model=UserListResponse)
async def get_users(
    session: SessionDep,
    current_user: CurrentAdminUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """管理员获取用户列表"""
    users = session.exec(select(User).offset(skip).limit(limit)).all()
    total = session.exec(select(User)).count()
    
    return UserListResponse(total=total, users=users)


# 管理员获取单个用户详情
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    session: SessionDep,
    current_user: CurrentAdminUser
):
    """管理员获取用户详情"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return user


# 管理员更新用户信息
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: SessionDep,
    current_user: CurrentAdminUser
):
    """管理员更新用户信息"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 用户名检查
    if user_data.username and user_data.username != user.username:
        db_user = session.exec(
            select(User).where(User.username == user_data.username)
        ).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        user.username = user_data.username
    
    # 邮箱检查
    if user_data.email and user_data.email != user.email:
        db_user = session.exec(
            select(User).where(User.email == user_data.email)
        ).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
        user.email = user_data.email
    
    # 密码更新
    if user_data.password:
        user.hashed_password = get_password_hash(user_data.password)
    
    # 是否激活
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    # 是否管理员
    if user_data.is_admin is not None:
        user.is_admin = user_data.is_admin
    
    # 更新时间
    user.updated_at = datetime.utcnow()
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user


# 管理员删除用户
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    session: SessionDep,
    current_user: CurrentAdminUser
):
    """管理员删除用户"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能删除自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除当前用户"
        )
    
    session.delete(user)
    session.commit() 