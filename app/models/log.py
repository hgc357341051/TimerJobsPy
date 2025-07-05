import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, get_table_name

if TYPE_CHECKING:
    from app.models.job import Job


class JobExecLog(Base):
    """任务执行日志模型"""

    __tablename__ = get_table_name("job_exec_logs")

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 基本信息
    time: Mapped[str] = mapped_column(String(50), nullable=False, comment="开始时间")
    end_time: Mapped[str] = mapped_column(String(50), nullable=False, comment="结束时间")
    job_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{get_table_name('jobs')}.id", ondelete="CASCADE"),
        nullable=False,
        comment="任务ID",
    )
    job_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="任务名称")
    status: Mapped[str] = mapped_column(String(20), nullable=False, comment="执行状态")
    duration_ms: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="执行时长(毫秒)"
    )

    # 执行信息
    mode: Mapped[str] = mapped_column(String(20), nullable=False, comment="执行模式")
    command: Mapped[str] = mapped_column(Text, nullable=False, comment="执行命令")

    # 命令执行结果
    exit_code: Mapped[Optional[int]] = mapped_column(Integer, comment="退出码")
    stdout: Mapped[Optional[str]] = mapped_column(Text, comment="标准输出")
    stderr: Mapped[Optional[str]] = mapped_column(Text, comment="错误输出")

    # HTTP请求结果
    http_url: Mapped[Optional[str]] = mapped_column(String(500), comment="HTTP URL")
    http_method: Mapped[Optional[str]] = mapped_column(String(10), comment="HTTP方法")
    http_status: Mapped[Optional[int]] = mapped_column(Integer, comment="HTTP状态码")
    http_resp: Mapped[Optional[str]] = mapped_column(Text, comment="HTTP响应内容")

    # 函数执行结果
    func_name: Mapped[Optional[str]] = mapped_column(String(100), comment="函数名称")
    func_args: Mapped[Optional[str]] = mapped_column(Text, comment="函数参数")
    func_result: Mapped[Optional[str]] = mapped_column(Text, comment="函数执行结果")

    # 错误信息
    error_msg: Mapped[Optional[str]] = mapped_column(Text, comment="错误信息")

    # 时间戳
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, comment="创建时间"
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        comment="更新时间",
    )

    # 关系
    job: Mapped["Job"] = relationship("Job", back_populates="logs")

    def __repr__(self) -> str:
        return (
            f"<JobExecLog(id={self.id}, job_id={self.job_id}, status='{self.status}')>"
        )
