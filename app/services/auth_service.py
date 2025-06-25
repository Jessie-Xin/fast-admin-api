import logging
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from sqlmodel import Session, select
from app.core.config import settings
from app.core.security import (
    create_access_token, generate_reset_token, get_password_hash, verify_password
)
from app.core.validators import validate_password
from app.models.user import User
from app.schemas.auth import PasswordChange, PasswordReset, PasswordResetRequest
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)

# 登录业务逻辑
def login_service(session: Session, username: str, password: str) -> Optional[User]:
    """登录业务逻辑，返回用户对象或 None"""
    user = session.exec(select(User).where(User.email == username)).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

# 创建访问令牌业务逻辑
def create_token_for_user(user: User) -> str:
    """为用户创建访问令牌"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(subject=str(user.id), expires_delta=access_token_expires)

# 用户注册业务逻辑
def register_user_service(user_data: UserCreate, session: Session) -> User:
    """注册新用户业务逻辑"""
    is_valid, error_messages = validate_password(user_data.password)
    if not is_valid:
        error_detail = ", ".join(error_messages)
        raise ValueError(f"密码不符合安全要求: {error_detail}")
    db_user = session.exec(select(User).where(User.username == user_data.username)).first()
    if db_user:
        raise ValueError("用户名已存在")
    db_email = session.exec(select(User).where(User.email == user_data.email)).first()
    if db_email:
        raise ValueError("邮箱已存在")
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=user_data.is_active,
        is_admin=user_data.is_admin,
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

# 密码重置请求业务逻辑
def password_reset_request_service(reset_request: PasswordResetRequest, session: Session) -> dict:
    """请求密码重置业务逻辑"""
    user = session.exec(select(User).where(User.email == reset_request.email)).first()
    if not user:
        return {"message": "如果该邮箱存在，密码重置链接已发送"}
    reset_token = generate_reset_token()
    token_expires = datetime.utcnow() + timedelta(hours=24)
    user.reset_token = reset_token
    user.reset_token_expires = token_expires
    session.add(user)
    session.commit()
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    logger.info(f"生成密码重置链接: {reset_url}")
    return {"message": "密码重置链接已发送到您的邮箱", "reset_url": reset_url, "token": reset_token}

# 密码重置业务逻辑
def reset_password_service(reset_data: PasswordReset, session: Session):
    """重置密码业务逻辑"""
    user = session.exec(select(User).where(User.reset_token == reset_data.token)).first()
    if not user:
        raise ValueError("无效的重置令牌")
    if user.reset_token_expires is None or user.reset_token_expires < datetime.utcnow():
        raise ValueError("重置令牌已过期")
    is_valid, error_messages = validate_password(reset_data.new_password)
    if not is_valid:
        error_detail = ", ".join(error_messages)
        raise ValueError(f"密码不符合安全要求: {error_detail}")
    user.hashed_password = get_password_hash(reset_data.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    session.add(user)
    session.commit()
    return {"message": "密码重置成功"}

# 修改密码业务逻辑
def change_password_service(password_data: PasswordChange, user: User, session: Session):
    """修改密码业务逻辑"""
    if not verify_password(password_data.current_password, user.hashed_password):
        raise ValueError("当前密码不正确")
    is_valid, error_messages = validate_password(password_data.new_password)
    if not is_valid:
        error_detail = ", ".join(error_messages)
        raise ValueError(f"密码不符合安全要求: {error_detail}")
    user.hashed_password = get_password_hash(password_data.new_password)
    session.add(user)
    session.commit()
    return {"message": "密码修改成功"}

# 通过 token 获取用户业务逻辑
def get_user_by_token_service(token: str, session: Session) -> Optional[User]:
    """通过 token 获取用户业务逻辑"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    user = session.get(User, int(user_id))
    return user 