from sqlmodel import Session, create_engine

from app.core.config import settings

# 创建SQLAlchemy引擎
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False},  # SQLite 特有配置
)


# 获取数据库会话
def get_session():
    """提供数据库会话依赖"""
    with Session(engine) as session:
        yield session
