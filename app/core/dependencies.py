from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import get_session
from app.models.user import User

# OAuth2密码流认证
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# 数据库会话依赖
SessionDep = Annotated[Session, Depends(get_session)]

async def get_current_user(
    session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    """获取当前认证用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码JWT令牌
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 查询用户
    user = session.exec(select(User).where(User.id == user_id)).first()
    if user is None:
        raise credentials_exception
    
    return user

# 当前用户依赖
CurrentUser = Annotated[User, Depends(get_current_user)]

async def get_current_active_user(
    current_user: CurrentUser,
) -> User:
    """获取当前激活用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )
    return current_user

# 当前激活用户依赖
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]

async def get_current_admin_user(
    current_user: CurrentActiveUser,
) -> User:
    """获取当前管理员用户"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限",
        )
    return current_user

# 当前管理员用户依赖
CurrentAdminUser = Annotated[User, Depends(get_current_admin_user)] 