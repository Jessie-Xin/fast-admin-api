from datetime import datetime, UTC
import logging
from sqlmodel import Session, select, func
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

# 设置日志
logger = logging.getLogger(__name__)

# 获取分类列表业务逻辑
def get_categories_service(session: Session, skip: int = 0, limit: int = 100):
    """获取分类列表业务逻辑"""
    try:
        # 获取分页数据
        categories_query = select(Category).offset(skip).limit(limit)
        categories = session.exec(categories_query).all()
        
        # 获取总数
        count_query = select(func.count(Category.id))
        total_result = session.exec(count_query).first()
        total = int(total_result) if total_result is not None else 0
        
        logger.info(f"获取分类列表: 总数={total}, 返回={len(categories)}")
        return total, categories
    except Exception as e:
        logger.error(f"获取分类列表错误: {str(e)}", exc_info=True)
        raise

# 获取分类详情业务逻辑
def get_category_service(categoryId: int, session: Session):
    """获取分类详情业务逻辑"""
    return session.get(Category, categoryId)

# 检查分类名是否存在
def check_category_exists(session: Session, name: str):
    """检查分类名是否存在"""
    db_category = session.exec(select(Category).where(Category.name == name)).first()
    return db_category is not None

# 创建分类业务逻辑
def create_category_service(category_data: CategoryCreate, session: Session):
    """创建分类业务逻辑"""
    new_category = Category(**category_data.model_dump())
    session.add(new_category)
    session.commit()
    session.refresh(new_category)
    return new_category

# 更新分类业务逻辑
def update_category_service(category: Category, category_data: CategoryUpdate, session: Session):
    """更新分类业务逻辑"""
    if category_data.name and category_data.name != category.name:
        category.name = category_data.name
    if category_data.description is not None:
        category.description = category_data.description
    category.updated_at = datetime.now(UTC)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

# 删除分类业务逻辑
def delete_category_service(category: Category, session: Session):
    """删除分类业务逻辑"""
    session.delete(category)
    session.commit() 