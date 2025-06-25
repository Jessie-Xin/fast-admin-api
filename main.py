import uvicorn

from app.core.config import settings

if __name__ == "__main__":
    # 启动Uvicorn服务器
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
