"""
Pydantic 模型定义
包含中文提示和自定义验证
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class JobBase(BaseModel):
    """任务基础模型"""

    name: str = Field(..., min_length=1, max_length=100, description="任务名称")
    desc: Optional[str] = Field(None, max_length=500, description="任务描述")
    cron_expr: str = Field(..., description="cron表达式")
    mode: str = Field(default="http", description="执行模式")
    command: str = Field(..., description="执行命令或URL")
    allow_mode: int = Field(
        default=0, ge=0, le=2, description="执行模式: 0=并发, 1=串行, 2=立即执行"
    )
    max_run_count: Optional[int] = Field(None, ge=0, description="最大执行次数，0表示无限制")
    state: int = Field(default=0, ge=0, le=2, description="任务状态: 0=停止, 1=运行, 2=完成")

    @field_validator("cron_expr")
    @classmethod
    def validate_cron_expr(cls, v: str) -> str:
        """验证cron表达式"""
        if not v:
            raise ValueError("cron表达式不能为空")

        # 简单的cron表达式验证
        parts = v.split()
        if len(parts) not in [5, 6]:
            raise ValueError("cron表达式格式错误，应为5个字段（分 时 日 月 周）或6个字段（秒 分 时 日 月 周）")

        # 这里可以添加更详细的cron表达式验证逻辑
        return v

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        """验证执行模式"""
        valid_modes = ["http", "command", "func", "function"]
        if v not in valid_modes:
            raise ValueError(f'无效的执行模式，支持的模式：{", ".join(valid_modes)}')
        return v

    @field_validator("allow_mode")
    @classmethod
    def validate_allow_mode(cls, v: int) -> int:
        """验证执行模式"""
        if v not in [0, 1, 2]:
            raise ValueError("无效的执行模式，支持：0=并发, 1=串行, 2=立即执行")
        return v

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: int) -> int:
        """验证任务状态"""
        if v not in [0, 1, 2]:
            raise ValueError("无效的任务状态，支持：0=停止, 1=运行, 2=完成")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "测试任务",
                "desc": "这是一个测试任务",
                "cron_expr": "0 0 * * *",
                "mode": "http",
                "command": "https://api.example.com/test",
                "allow_mode": 0,
                "max_run_count": None,
                "state": 0,
            }
        }
    )


class JobCreate(BaseModel):
    name: str = Field(..., description="任务名称")
    desc: Optional[str] = Field(None, description="任务描述")
    cron_expr: Optional[str] = Field(None, description="cron表达式，trigger_type=cron时必填")
    trigger_type: Literal["cron", "interval"] = Field(
        "cron", description="触发器类型：cron/interval，interval为秒级调度"
    )
    interval_seconds: Optional[int] = Field(0, description="interval模式下的间隔秒数，单位秒")
    mode: str = Field(..., description="执行模式(function/http)")
    command: str = Field(..., description="执行命令或URL")
    allow_mode: int = Field(0, description="并发模式")
    max_run_count: int = Field(0, description="最大执行次数，0为无限制")
    state: int = Field(1, description="任务状态 1=运行 0=等待 2=停止")

    @field_validator("cron_expr")
    @classmethod
    def validate_cron_expr(cls, v: str) -> str:
        if not v or len(v.split()) not in [5, 6]:
            raise ValueError("cron表达式格式错误，应为5个字段（分 时 日 月 周）或6个字段（秒 分 时 日 月 周）")
        return v

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        allowed = {"http", "command", "function", "func"}
        if v not in allowed:
            raise ValueError(f"mode必须为{allowed}")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("任务名称不能为空")
        return v

    @field_validator("command")
    @classmethod
    def validate_command(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("command不能为空")
        return v


class JobUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, description="任务名称")
    desc: Optional[str] = Field(None, description="任务描述")
    cron_expr: Optional[str] = Field(None, description="cron表达式")
    trigger_type: Optional[Literal["cron", "interval"]] = Field(
        None, description="触发器类型：cron/interval，interval为秒级调度"
    )
    interval_seconds: Optional[int] = Field(None, description="interval模式下的间隔秒数，单位秒")
    mode: Optional[str] = Field(None, description="执行模式")
    command: Optional[str] = Field(None, description="执行命令或URL")
    allow_mode: Optional[int] = Field(None, description="并发模式")
    max_run_count: Optional[int] = Field(None, description="最大执行次数")
    state: Optional[int] = Field(None, description="任务状态")

    @field_validator("cron_expr")
    @classmethod
    def validate_cron_expr(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not v.strip() or len(v.split()) not in [5, 6]):
            raise ValueError("cron表达式格式错误，应为5个字段（分 时 日 月 周）或6个字段（秒 分 时 日 月 周）")
        return v

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = {"http", "command", "function", "func"}
            if v not in allowed:
                raise ValueError(f"mode必须为{allowed}")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("任务名称不能为空")
        return v

    @field_validator("command")
    @classmethod
    def validate_command(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("command不能为空")
        return v


class JobResponse(JobBase):
    """任务响应模型"""

    id: int = Field(..., description="任务ID")
    run_count: int = Field(..., description="已执行次数")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class JobListResponse(BaseModel):
    """任务列表响应模型"""

    total: int = Field(..., description="总数量")
    items: List[JobResponse] = Field(..., description="任务列表")


class IPControlRequest(BaseModel):
    """IP控制请求模型"""

    ip: str = Field(..., description="IP地址")
    type: str = Field(..., description="类型: whitelist=白名单, blacklist=黑名单")

    @field_validator("ip")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        """验证IP地址格式"""
        ip_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        if not re.match(ip_pattern, v):
            raise ValueError("IP地址格式不正确")

        parts = v.split(".")
        for part in parts:
            if not 0 <= int(part) <= 255:
                raise ValueError("IP地址范围不正确")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """验证类型"""
        if v not in ["whitelist", "blacklist"]:
            raise ValueError("类型必须是 whitelist 或 blacklist")
        return v

    model_config = ConfigDict(
        json_schema_extra={"example": {"ip": "192.168.1.1", "type": "whitelist"}}
    )


class ResponseModel(BaseModel):
    """通用响应模型"""

    code: int = Field(..., description="状态码")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")


class PaginationParams(BaseModel):
    """分页参数模型"""

    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=10, ge=1, le=100, description="每页数量")


class AdminBase(BaseModel):
    username: str
    password: str
    role: str = "admin"
    is_active: bool = True


class AdminCreate(AdminBase):
    pass


class AdminUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class AdminResponse(AdminBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AdminResponse


class SystemStatus(BaseModel):
    total_jobs: int
    running_jobs: int
    stopped_jobs: int
    waiting_jobs: int
    scheduler_running: bool


class IPControlStatus(BaseModel):
    whitelist: List[str]
    blacklist: List[str]


class FunctionInfo(BaseModel):
    name: str
    description: str
    parameters: Optional[Dict[str, Any]] = None
