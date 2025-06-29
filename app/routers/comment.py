from fastapi import APIRouter, HTTPException, Query, status
import logging

from app.core.dependencies import (CurrentActiveUser, SessionDep)
from app.schemas.comment import (CommentCreate, CommentListResponse,
                                 CommentResponse, CommentUpdate)
from app.services.comment_service import (
    get_comments_service,
    get_comment_service,
    create_comment_service,
    update_comment_service,
    delete_comment_service,
)

# 设置日志
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/comments", tags=["comments"])


# 获取评论列表
@router.get("/", response_model=CommentListResponse)
async def get_comments(
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    postId: int = None,
):
    """获取评论列表，可按文章ID筛选"""
    try:
        # 获取评论列表和总数
        total, comments = get_comments_service(session, skip, limit, postId)
        logger.info(f"获取评论列表: 总数={total}, 返回={len(comments)}")
        
        # 将SQLModel对象转换为Pydantic响应模型
        formatted_comments = [CommentResponse.model_validate(comment, from_attributes=True) for comment in comments]
        logger.info(f"格式化后的评论列表长度: {len(formatted_comments)}")
        
        # 构建并返回响应
        response = CommentListResponse(total=total, comments=formatted_comments)
        return response
    except Exception as e:
        logger.error(f"获取评论列表出错: {str(e)}", exc_info=True)
        raise


# 获取评论详情
@router.get("/{commentId}", response_model=CommentResponse)
async def get_comment(commentId: int, session: SessionDep):
    """获取评论详情"""
    comment = get_comment_service(commentId, session)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")
    return comment


# 创建评论（需要登录）
@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_data: CommentCreate, session: SessionDep, current_user: CurrentActiveUser
):
    """创建评论"""
    new_comment = create_comment_service(comment_data, session, current_user.id)
    if not new_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
    return new_comment


# 更新评论（作者本人或管理员）
@router.put("/{commentId}", response_model=CommentResponse)
async def update_comment(
    commentId: int,
    comment_data: CommentUpdate,
    session: SessionDep,
    current_user: CurrentActiveUser,
):
    """更新评论"""
    comment = get_comment_service(commentId, session)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")
    if comment.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="没有权限更新此评论"
        )
    updated_comment = update_comment_service(comment, comment_data, session)
    return updated_comment


# 删除评论（作者本人或管理员）
@router.delete("/{commentId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    commentId: int, session: SessionDep, current_user: CurrentActiveUser
):
    """删除评论"""
    comment = get_comment_service(commentId, session)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")
    if comment.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="没有权限删除此评论"
        )
    delete_comment_service(comment, session)
