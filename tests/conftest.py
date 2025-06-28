"""
测试配置文件
配置pytest测试环境
"""

import os
import tempfile
from typing import Any, Generator

import pytest
from app.deps import get_db
from app.main import app
from app.models.admin import Admin
from app.models.base import Base
from app.models.job import Job
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture(scope="session")
def test_db() -> Generator[str, None, None]:
    """创建测试数据库"""
    # 创建临时数据库文件
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # 设置测试数据库配置
    os.environ["DATABASE_TYPE"] = "sqlite"
    os.environ["DATABASE_SQLITE_PATH"] = path

    yield path

    # 清理
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture(scope="session")
def engine(test_db: str) -> Generator[Any, None, None]:
    """创建数据库引擎"""
    engine = create_engine(f"sqlite:///{test_db}")
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine: Any) -> Generator[Session, None, None]:
    """创建数据库会话"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """创建测试客户端"""

    # 覆盖依赖
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides = {}
    app.dependency_overrides[get_db] = override_get_db

    # 为测试环境禁用IP控制
    os.environ["IP_WHITELIST"] = "127.0.0.1,localhost,testclient"

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_job(db_session: Session) -> Job:
    """创建示例任务"""
    job = Job(
        name="测试任务",
        cron_expr="0 0 * * *",
        command="https://example.com",
        mode="http",
        allow_mode=0,
        state=0,
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


@pytest.fixture
def sample_admin(db_session: Session) -> Admin:
    """创建示例管理员"""
    admin = Admin(username="test_admin", password="test_password", role="admin")
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def valid_job_data() -> dict[str, Any]:
    """有效的任务数据"""
    return {
        "name": "测试任务",
        "cron_expr": "0 0 * * *",
        "command": "https://example.com",
        "mode": "http",
        "allow_mode": 0,
        "state": 0,
    }


@pytest.fixture
def invalid_job_data() -> dict[str, Any]:
    """无效的任务数据"""
    return {
        "name": "",
        "cron_expr": "invalid_cron",
        "command": "",
        "mode": "invalid_mode",
    }
