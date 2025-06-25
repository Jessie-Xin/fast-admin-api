from datetime import datetime, UTC
import logging
from sqlmodel import Session, select, func
from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import CommentCreate, CommentUpdate

# 设置日志
logger = logging.getLogger(__name__)

# 获取评论列表业务逻辑
def get_comments_service(session: Session, skip: int = 0, limit: int = 100, postId: int = None):
    """获取评论列表业务逻辑"""
    try:
        # 构建基础查询
        query = select(Comment)
        count_query = select(func.count(Comment.id))
        
        # 添加过滤条件
        if postId:
            query = query.filter(Comment.post_id == postId)
            count_query = count_query.filter(Comment.post_id == postId)
        
        # 获取总数
        total_result = session.exec(count_query).first()
        total = int(total_result) if total_result is not None else 0
        
        # 获取分页数据
        comments_query = query.order_by(Comment.created_at.desc()).offset(skip).limit(limit)
        comments = session.exec(comments_query).all()
        
        logger.info(f"获取评论列表: 总数={total}, 返回={len(comments)}")
        return total, comments
    except Exception as e:
        logger.error(f"获取评论列表错误: {str(e)}", exc_info=True)
        raise

# 获取评论详情业务逻辑
def get_comment_service(commentId: int, session: Session):
    """获取评论详情业务逻辑"""
    return session.get(Comment, commentId)

# 创建评论业务逻辑
def create_comment_service(comment_data: CommentCreate, session: Session, user_id: int):
    """创建评论业务逻辑"""
    post = session.get(Post, comment_data.post_id)
    if not post:
        return None
    new_comment = Comment(
        content=comment_data.content,
        author_id=user_id,
        post_id=comment_data.post_id,
    )
    session.add(new_comment)
    session.commit()
    session.refresh(new_comment)
    return new_comment

# 更新评论业务逻辑
def update_comment_service(comment: Comment, comment_data: CommentUpdate, session: Session):
    """更新评论业务逻辑"""
    comment.content = comment_data.content
    comment.updated_at = datetime.now(UTC)
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment

# 删除评论业务逻辑
def delete_comment_service(comment: Comment, session: Session):
    """删除评论业务逻辑"""
    session.delete(comment)
    session.commit() 