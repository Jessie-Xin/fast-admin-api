from fastapi import APIRouter, HTTPException, Query, status
import logging

from app.core.dependencies import (CurrentAdminUser,
                                   SessionDep)
from app.schemas.tag import TagCreate, TagListResponse, TagResponse, TagUpdate
from app.services.tag_service import (
    get_tags_service,
    get_tag_service,
    check_tag_exists,
    create_tag_service,
    update_tag_service,
    delete_tag_service,
)

# 设置日志
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tags", tags=["tags"])


# 获取标签列表
@router.get("/", response_model=TagListResponse)
async def get_tags(
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """获取标签列表"""
    try:
        # 获取标签列表和总数
        total, tags = get_tags_service(session, skip, limit)
        logger.info(f"获取标签列表: 总数={total}, 返回={len(tags)}")
        
        # 将SQLModel对象转换为Pydantic响应模型
        formatted_tags = [TagResponse.model_validate(tag, from_attributes=True) for tag in tags]
        logger.info(f"格式化后的标签列表长度: {len(formatted_tags)}")
        
        # 构建并返回响应
        response = TagListResponse(total=total, tags=formatted_tags)
        return response
    except Exception as e:
        logger.error(f"获取标签列表出错: {str(e)}", exc_info=True)
        raise


# 获取标签详情
@router.get("/{tagId}", response_model=TagResponse)
async def get_tag(tagId: int, session: SessionDep):
    """获取标签详情"""
    tag = get_tag_service(tagId, session)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="标签不存在")
    return tag


# 创建标签（需要管理员权限）
@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate, session: SessionDep, current_user: CurrentAdminUser
):
    """创建标签"""
    if check_tag_exists(session, tag_data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="标签名已存在"
        )
    new_tag = create_tag_service(tag_data, session)
    return new_tag


# 更新标签（需要管理员权限）
@router.put("/{tagId}", response_model=TagResponse)
async def update_tag(
    tagId: int, tag_data: TagUpdate, session: SessionDep, current_user: CurrentAdminUser
):
    """更新标签"""
    tag = get_tag_service(tagId, session)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="标签不存在")
    if tag_data.name != tag.name and check_tag_exists(session, tag_data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="标签名已存在"
        )
    updated_tag = update_tag_service(tag, tag_data, session)
    return updated_tag


# 删除标签（需要管理员权限）
@router.delete("/{tagId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tagId: int, session: SessionDep, current_user: CurrentAdminUser):
    """删除标签"""
    tag = get_tag_service(tagId, session)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="标签不存在")
    delete_tag_service(tag, session)
