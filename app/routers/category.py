from fastapi import APIRouter, HTTPException, Query, status
import logging

from app.core.dependencies import (CurrentAdminUser,
                                   SessionDep)
from app.schemas.category import (CategoryCreate, CategoryListResponse,
                                  CategoryResponse, CategoryUpdate)
from app.services.category_service import (
    get_categories_service,
    get_category_service,
    check_category_exists,
    create_category_service,
    update_category_service,
    delete_category_service,
)

# 设置日志
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/categories", tags=["categories"])


# 获取分类列表
@router.get("/", response_model=CategoryListResponse)
async def get_categories(
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """获取分类列表"""
    try:
        # 获取分类列表和总数
        total, categories = get_categories_service(session, skip, limit)
        logger.info(f"获取分类列表: 总数={total}, 返回={len(categories)}")
        
        # 将SQLModel对象转换为Pydantic响应模型
        formatted_categories = [CategoryResponse.model_validate(category, from_attributes=True) for category in categories]
        logger.info(f"格式化后的分类列表长度: {len(formatted_categories)}")
        
        # 构建并返回响应
        response = CategoryListResponse(total=total, categories=formatted_categories)
        return response
    except Exception as e:
        logger.error(f"获取分类列表出错: {str(e)}", exc_info=True)
        raise


# 获取分类详情
@router.get("/{categoryId}", response_model=CategoryResponse)
async def get_category(categoryId: int, session: SessionDep):
    """获取分类详情"""
    category = get_category_service(categoryId, session)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在")
    return category


# 创建分类（需要管理员权限）
@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate, session: SessionDep, current_user: CurrentAdminUser
):
    """创建分类"""
    if check_category_exists(session, category_data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="分类名已存在"
        )
    new_category = create_category_service(category_data, session)
    return new_category


# 更新分类（需要管理员权限）
@router.put("/{categoryId}", response_model=CategoryResponse)
async def update_category(
    categoryId: int,
    category_data: CategoryUpdate,
    session: SessionDep,
    current_user: CurrentAdminUser,
):
    """更新分类"""
    category = get_category_service(categoryId, session)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在")
    if category_data.name and category_data.name != category.name and check_category_exists(session, category_data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="分类名已存在"
        )
    updated_category = update_category_service(category, category_data, session)
    return updated_category


# 删除分类（需要管理员权限）
@router.delete("/{categoryId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    categoryId: int, session: SessionDep, current_user: CurrentAdminUser
):
    """删除分类"""
    category = get_category_service(categoryId, session)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在")
    delete_category_service(category, session)
