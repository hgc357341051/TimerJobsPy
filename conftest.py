"""
pytest 配置文件
包含测试用的fixture和配置
"""

import pytest
import tempfile
import os
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.deps import get_db
from app.models.base import Base
from app.models.job import Job
from app.models.log import JobExecLog
from app.models.admin import Admin
from app.core.scheduler import scheduler


# 创建内存数据库用于测试
@pytest.fixture(scope="session")
def test_engine():
    """创建测试数据库引擎"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine


@pytest.fixture(scope="session")
def test_db_session(test_engine):
    """创建测试数据库会话"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    return TestingSessionLocal


@pytest.fixture(scope="function")
def db_session(test_engine, test_db_session):
    """每个测试函数的数据库会话"""
    # 创建表
    Base.metadata.create_all(bind=test_engine)

    # 创建会话
    session = test_db_session()

    yield session

    # 清理
    session.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session) -> Generator:
    """测试客户端"""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sample_job(db_session) -> Job:
    """创建示例任务"""
    job = Job(
        name="测试任务",
        desc="用于测试的任务",
        cron_expr="0 0 * * *",
        mode="http",
        command="https://httpbin.org/get",
        allow_mode=0,
        max_run_count=5,
        run_count=0,
        state=1,
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


@pytest.fixture(scope="function")
def sample_admin(db_session) -> Admin:
    """创建示例管理员"""
    admin = Admin(
        username="test_admin",
        password="test_password",
        email="test@example.com",
        role="admin",
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def temp_dir():
    """临时目录"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(scope="function")
def mock_scheduler():
    """模拟调度器"""
    original_start = scheduler.start
    original_shutdown = scheduler.shutdown

    # 模拟调度器方法
    scheduler.start = lambda: None
    scheduler.shutdown = lambda wait=False: None

    yield scheduler

    # 恢复原始方法
    scheduler.start = original_start
    scheduler.shutdown = original_shutdown


# 测试数据
@pytest.fixture
def valid_job_data():
    """有效的任务数据"""
    return {
        "name": "测试任务",
        "desc": "这是一个测试任务",
        "cron_expr": "0 0 * * *",
        "mode": "http",
        "command": "https://httpbin.org/get",
        "allow_mode": 0,
        "max_run_count": 10,
    }


@pytest.fixture
def invalid_job_data():
    """无效的任务数据"""
    return {
        "name": "",  # 空名称
        "cron_expr": "invalid",  # 无效cron表达式
        "mode": "invalid_mode",  # 无效模式
        "command": "",
    }


@pytest.fixture
def http_job_data():
    """HTTP任务数据"""
    return {
        "name": "HTTP测试任务",
        "cron_expr": "*/5 * * * *",  # 每5分钟
        "mode": "http",
        "command": "https://httpbin.org/status/200",
    }


@pytest.fixture
def command_job_data():
    """命令任务数据"""
    return {
        "name": "命令测试任务",
        "cron_expr": "0 0 * * *",
        "mode": "command",
        "command": "echo 'Hello World'",
    }


@pytest.fixture
def func_job_data():
    """函数任务数据"""
    return {
        "name": "函数测试任务",
        "cron_expr": "0 0 * * *",
        "mode": "func",
        "command": "test_function",
    }
