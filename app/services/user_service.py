from datetime import datetime
from sqlmodel import Session, select
from app.models.user import User
from app.schemas.user import UserUpdate
from app.core.security import get_password_hash

# 获取用户列表业务逻辑
def get_users_service(session: Session, skip: int = 0, limit: int = 100):
    """获取用户列表业务逻辑"""
    users = session.exec(select(User).offset(skip).limit(limit)).all()
    total = session.exec(select(User)).count()
    return total, users

# 获取单个用户详情业务逻辑
def get_user_service(userId: int, session: Session):
    """获取单个用户详情业务逻辑"""
    return session.get(User, userId)

# 检查用户名或邮箱是否已存在
def check_user_exists(session: Session, username: str = None, email: str = None):
    """检查用户名或邮箱是否已存在"""
    if username:
        db_user = session.exec(select(User).where(User.username == username)).first()
        if db_user:
            return True
    if email:
        db_user = session.exec(select(User).where(User.email == email)).first()
        if db_user:
            return True
    return False

# 更新用户信息业务逻辑
def update_user_service(user: User, user_data: UserUpdate):
    """更新用户信息业务逻辑"""
    if user_data.username and user_data.username != user.username:
        user.username = user_data.username
    if user_data.email and user_data.email != user.email:
        user.email = user_data.email
    if user_data.password:
        user.hashed_password = get_password_hash(user_data.password)
    if hasattr(user_data, 'is_active') and user_data.is_active is not None:
        user.is_active = user_data.is_active
    if hasattr(user_data, 'is_admin') and user_data.is_admin is not None:
        user.is_admin = user_data.is_admin
    user.updated_at = datetime.utcnow()
    return user

# 删除用户业务逻辑
def delete_user_service(user: User, session: Session):
    """删除用户业务逻辑"""
    session.delete(user)
    session.commit() 