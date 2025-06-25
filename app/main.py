from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel

from app.core.config import settings
from app.core.database import engine
from app.core.logging_config import setup_logging
from app.routers import (auth_router, category_router, comment_router,
                         dashboard_router, post_router, tag_router,
                         user_router)

# 设置日志
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动时创建数据库表（仅开发时使用）"""
    logger.info(f"正在启动 {settings.APP_NAME} 应用程序...")
    if settings.DEBUG:
        SQLModel.metadata.create_all(engine)
    yield
    logger.info(f"{settings.APP_NAME} 应用程序正在关闭...")


# 创建FastAPI实例
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误"""
    # 提取错误信息
    error_messages = []
    for error in exc.errors():
        loc = " -> ".join([str(l) for l in error["loc"]])
        msg = error["msg"]
        error_messages.append(f"{loc}: {msg}")

    error_detail = "，".join(error_messages)
    logger.warning(f"请求参数验证失败: {error_detail}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": error_detail},
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有请求"""
    logger.debug(f"收到请求: {request.method} {request.url}")
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"处理请求时出错: {request.method} {request.url} - {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "服务器内部错误，请稍后重试"},
        )


# 注册路由器
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(category_router)
app.include_router(tag_router)
app.include_router(post_router)
app.include_router(comment_router)
app.include_router(dashboard_router)


# 健康检查接口
@app.get("/", tags=["health"])
async def health_check():
    """API健康检查接口"""
    return {"status": "ok", "message": f"Welcome to {settings.APP_NAME} API!"}
