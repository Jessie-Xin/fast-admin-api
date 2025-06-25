import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core.database import get_session
from app.core.security import get_password_hash
from app.main import app
from app.models.user import User


# 使用内存数据库进行测试
@pytest.fixture(name="engine")
def engine_fixture():
    """创建测试用的SQLite内存数据库引擎"""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine):
    """创建测试用的数据库会话"""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    """创建测试客户端，覆盖数据库会话依赖"""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session):
    """创建测试用户"""
    # 为测试用户生成哈希密码
    hashed_password = get_password_hash("password")

    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hashed_password,
        is_active=True,
        is_admin=False,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
