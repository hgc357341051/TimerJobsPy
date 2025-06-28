from typing import Generator

from app.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

engine = create_engine(
    Config.get_database_url(),
    **Config.get_database_engine_options(),
    connect_args=(
        {"check_same_thread": False} if "sqlite" in Config.get_database_url() else {}
    ),
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
