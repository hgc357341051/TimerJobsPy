import datetime
from typing import Optional

from app.models.base import Base, get_table_name
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class Job(Base):
    __tablename__ = get_table_name("jobs")

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="任务名称")
    desc: Mapped[Optional[str]] = mapped_column(Text, comment="任务描述")
    cron_expr: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="cron表达式"
    )
    mode: Mapped[str] = mapped_column(
        String(20), nullable=False, default="http", comment="执行模式"
    )
    command: Mapped[str] = mapped_column(Text, nullable=False, comment="执行命令或URL")
    state: Mapped[int] = mapped_column(Integer, default=0, comment="任务状态")
    allow_mode: Mapped[int] = mapped_column(Integer, default=0, comment="执行模式")
    max_run_count: Mapped[int] = mapped_column(
        Integer, default=0, comment="最大执行次数"
    )
    run_count: Mapped[int] = mapped_column(Integer, default=0, comment="已执行次数")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, comment="创建时间"
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        comment="更新时间",
    )
    trigger_type: Mapped[str] = mapped_column(
        String(20),
        default="cron",
        comment="触发器类型：cron/interval，interval为秒级调度",
    )
    interval_seconds: Mapped[int] = mapped_column(
        Integer, default=0, comment="interval模式下的间隔秒数，单位秒"
    )
