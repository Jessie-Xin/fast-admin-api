from fastapi import APIRouter, Depends
from sqlmodel import select

from app.core.dependencies import CurrentAdminUser, CurrentActiveUser, SessionDep
from app.models.category import Category
from app.models.comment import Comment
from app.models.post import Post
from app.models.tag import Tag
from app.models.user import User
from app.schemas.dashboard import DashboardSummary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


# 获取仪表盘摘要数据
@router.get("/summary", response_model=DashboardSummary)
async def get_summary(
    session: SessionDep,
    current_user: CurrentActiveUser
):
    """获取仪表盘摘要数据"""
    # 统计各项数量
    total_posts = session.exec(select(Post)).count()
    total_categories = session.exec(select(Category)).count()
    total_tags = session.exec(select(Tag)).count()
    total_comments = session.exec(select(Comment)).count()
    total_users = session.exec(select(User)).count()
    
    # 最近文章
    recent_posts = session.exec(
        select(Post).order_by(Post.created_at.desc()).limit(5)
    ).all()
    
    # 最近评论
    recent_comments = session.exec(
        select(Comment).order_by(Comment.created_at.desc()).limit(5)
    ).all()
    
    return DashboardSummary(
        total_posts=total_posts,
        total_categories=total_categories,
        total_tags=total_tags,
        total_comments=total_comments,
        total_users=total_users,
        recent_posts=recent_posts,
        recent_comments=recent_comments
    ) 