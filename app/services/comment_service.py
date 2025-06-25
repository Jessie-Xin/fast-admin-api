from datetime import datetime
from sqlmodel import Session, select
from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import CommentCreate, CommentUpdate

# 获取评论列表业务逻辑
def get_comments_service(session: Session, skip: int = 0, limit: int = 100, postId: int = None):
    """获取评论列表业务逻辑"""
    query = select(Comment)
    if postId:
        query = query.filter(Comment.post_id == postId)
    total = len(session.exec(query).all())
    query = query.order_by(Comment.created_at.desc()).offset(skip).limit(limit)
    comments = session.exec(query).all()
    return total, comments

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
    comment.updated_at = datetime.utcnow()
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment

# 删除评论业务逻辑
def delete_comment_service(comment: Comment, session: Session):
    """删除评论业务逻辑"""
    session.delete(comment)
    session.commit() 