from datetime import datetime, UTC
import logging
from sqlmodel import Session, select, func
from app.models.user import User
from app.schemas.user import UserUpdate
from app.core.security import get_password_hash

# 设置日志
logger = logging.getLogger(__name__)

# 获取用户列表业务逻辑
def get_users_service(session: Session, skip: int = 0, limit: int = 100):
    """获取用户列表业务逻辑"""
    try:
        # 获取分页用户列表
        users_query = select(User).offset(skip).limit(limit)
        logger.info(f"用户查询: {users_query}")
        users = session.exec(users_query).all()
        logger.info(f"获取到用户列表: {len(users)} 条记录")
        
        # 获取用户总数
        total_query = select(func.count(User.id))
        logger.info(f"总数查询: {total_query}")
        total_result = session.exec(total_query).first()
        logger.info(f"获取到用户总数结果: {total_result}, 类型: {type(total_result)}")
        
        # 确保total是整数
        total = int(total_result) if total_result is not None else 0
        logger.info(f"最终用户总数: {total}")
        
        return total, users
    except Exception as e:
        logger.error(f"获取用户列表错误: {str(e)}", exc_info=True)
        raise

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
    user.updated_at = datetime.now(UTC)
    return user

# 删除用户业务逻辑
def delete_user_service(user: User, session: Session):
    """删除用户业务逻辑"""
    session.delete(user)
    session.commit() 