from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from app.core.config import settings
from app.core.database import engine
from app.routers import (auth_router, category_router, comment_router,
                        dashboard_router, post_router, tag_router, user_router)

# 创建FastAPI实例
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由器
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(category_router)
app.include_router(tag_router)
app.include_router(post_router)
app.include_router(comment_router)
app.include_router(dashboard_router)


# 创建数据库表（开发时使用，生产应使用Alembic迁移）
@app.on_event("startup")
def on_startup():
    """应用启动时创建数据库表（仅开发时使用）"""
    if settings.DEBUG:
        SQLModel.metadata.create_all(engine)


# 健康检查接口
@app.get("/", tags=["health"])
async def health_check():
    """API健康检查接口"""
    return {"status": "ok", "message": f"Welcome to {settings.APP_NAME} API!"} 