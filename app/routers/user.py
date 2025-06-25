from datetime import datetime

from fastapi import APIRouter, Query, status

from app.core.dependencies import (CurrentActiveUser, CurrentAdminUser,
                                   CurrentUser, SessionDep)
from app.core.security import get_password_hash
from app.schemas.user import UserListResponse, UserResponse, UserUpdate
from app.services.user_service import (
    get_users_service,
    get_user_service,
    check_user_exists,
    update_user_service,
    delete_user_service,
)

router = APIRouter(prefix="/api/users", tags=["users"])


# 获取当前用户信息
@router.get("/me", response_model=UserResponse)
async def get_user_me(current_user: CurrentUser):
    """获取当前登录用户信息"""
    return current_user


# 更新当前用户信息
@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_data: UserUpdate, current_user: CurrentActiveUser, session: SessionDep
):
    """更新当前用户信息"""
    # 用户名检查
    if user_data.username and user_data.username != current_user.username:
        if check_user_exists(session, username=user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在"
            )
        current_user.username = user_data.username

    # 邮箱检查
    if user_data.email and user_data.email != current_user.email:
        if check_user_exists(session, email=user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已存在"
            )
        current_user.email = user_data.email

    # 密码更新
    if user_data.password:
        current_user.hashed_password = get_password_hash(user_data.password)

    # 更新时间
    current_user.updated_at = datetime.utcnow()

    updated_user = update_user_service(current_user, user_data)
    session.add(updated_user)
    session.commit()
    session.refresh(updated_user)

    return updated_user


# 管理员获取所有用户列表
@router.get("/", response_model=UserListResponse)
async def get_users(
    session: SessionDep,
    current_user: CurrentAdminUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """管理员获取用户列表"""
    total, users = get_users_service(session, skip, limit)
    return UserListResponse(total=total, users=users)


# 管理员获取单个用户详情
@router.get("/{userId}", response_model=UserResponse)
async def get_user(userId: int, session: SessionDep, current_user: CurrentAdminUser):
    """管理员获取用户详情"""
    user = get_user_service(userId, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    return user


# 管理员更新用户信息
@router.put("/{userId}", response_model=UserResponse)
async def update_user(
    userId: int,
    user_data: UserUpdate,
    session: SessionDep,
    current_user: CurrentAdminUser,
):
    """管理员更新用户信息"""
    user = get_user_service(userId, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # 用户名检查
    if user_data.username and user_data.username != user.username:
        if check_user_exists(session, username=user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在"
            )
        user.username = user_data.username

    # 邮箱检查
    if user_data.email and user_data.email != user.email:
        if check_user_exists(session, email=user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已存在"
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

    updated_user = update_user_service(user, user_data)
    session.add(updated_user)
    session.commit()
    session.refresh(updated_user)

    return updated_user


# 管理员删除用户
@router.delete("/{userId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(userId: int, session: SessionDep, current_user: CurrentAdminUser):
    """管理员删除用户"""
    user = get_user_service(userId, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # 不能删除自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="不能删除当前用户"
        )

    delete_user_service(user, session)
