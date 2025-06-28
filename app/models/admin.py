import datetime
from typing import Optional

from app.models.base import Base, get_table_name
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class Admin(Base):
    __tablename__ = get_table_name("admins")

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, comment="用户名"
    )
    password: Mapped[str] = mapped_column(String(100), nullable=False, comment="密码")
    email: Mapped[Optional[str]] = mapped_column(String(100), comment="邮箱")
    role: Mapped[str] = mapped_column(String(20), default="admin", comment="角色")
    status: Mapped[int] = mapped_column(Integer, default=1, comment="状态")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")
    last_login: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, comment="最后登录时间"
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, comment="创建时间"
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        comment="更新时间",
    )
