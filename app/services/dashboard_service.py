from sqlmodel import Session, select
from app.models.category import Category
from app.models.comment import Comment
from app.models.post import Post
from app.models.tag import Tag
from app.models.user import User
from app.schemas.dashboard import DashboardSummary

# 获取仪表盘摘要数据业务逻辑
def get_dashboard_summary_service(session: Session) -> DashboardSummary:
    """获取仪表盘摘要数据业务逻辑"""
    total_posts = session.exec(select(Post)).count()
    total_categories = session.exec(select(Category)).count()
    total_tags = session.exec(select(Tag)).count()
    total_comments = session.exec(select(Comment)).count()
    total_users = session.exec(select(User)).count()
    recent_posts = session.exec(
        select(Post).order_by(Post.created_at.desc()).limit(5)
    ).all()
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
        recent_comments=recent_comments,
    ) 