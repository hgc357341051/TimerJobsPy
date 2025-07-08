from contextlib import contextmanager
import logging
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import Config

# 配置日志
logger = logging.getLogger(__name__)

# 创建数据库引擎
try:
    engine = create_engine(
        Config.get_database_url(),
        **Config.get_database_engine_options(),
        connect_args=(
            {"check_same_thread": False} if "sqlite" in Config.get_database_url() else {}
        ),
    )
    
    # 为SQLite添加外键支持
    if "sqlite" in Config.get_database_url():
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
            
    logger.info(f"数据库引擎已创建: {Config.DATABASE_TYPE}")
except Exception as e:
    logger.error(f"创建数据库引擎失败: {e}")
    raise

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI依赖函数，用于获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"数据库会话异常: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """上下文管理器，用于在非API环境中获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"数据库会话异常: {e}")
        db.rollback()
        raise
    finally:
        db.close()
