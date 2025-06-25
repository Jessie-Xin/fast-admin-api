from app.routers.auth import router as auth_router
from app.routers.category import router as category_router
from app.routers.comment import router as comment_router
from app.routers.dashboard import router as dashboard_router
from app.routers.post import router as post_router
from app.routers.tag import router as tag_router
from app.routers.user import router as user_router

__all__ = [
    "auth_router",
    "user_router",
    "category_router",
    "tag_router",
    "post_router",
    "comment_router",
    "dashboard_router",
]
