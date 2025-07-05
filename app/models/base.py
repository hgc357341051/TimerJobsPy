from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import declarative_base

from app.config import Config

Base = declarative_base()

T = TypeVar("T")


class BaseResponse(BaseModel):
    """基础响应模型"""

    model_config = ConfigDict(from_attributes=True)


class StandardResponse(BaseResponse):
    """标准API响应格式"""

    code: int = 200
    msg: str = "操作成功"
    data: Optional[Any] = None


class PaginatedResponse(BaseResponse, Generic[T]):
    """分页响应格式"""

    code: int = 200
    msg: str = "获取成功"
    data: List[T]
    total: int
    page_total: int
    page: int
    page_size: int


class ErrorResponse(BaseResponse):
    """错误响应格式"""

    code: int = 400
    msg: str = "操作失败"
    data: Optional[Any] = None


def get_table_name(name: str) -> str:
    """获取带前缀的表名"""
    return f"{Config.DATABASE_SQLITE_TABLEPREFIX}{name}"


def success_response(data: Any = None, msg: str = "操作成功") -> Dict[str, Any]:
    """成功响应"""
    return {"code": 200, "msg": msg, "data": data}


def error_response(
    msg: str = "操作失败", code: int = 400, data: Any = None
) -> Dict[str, Any]:
    """错误响应"""
    return {"code": code, "msg": msg, "data": data}


def paginated_response(
    data: List[Any], total: int, page: int, page_size: int, msg: str = "获取成功"
) -> Dict[str, Any]:
    """分页响应"""
    page_total = (total + page_size - 1) // page_size  # 计算总页数
    return {
        "code": 200,
        "msg": msg,
        "data": data,
        "total": total,
        "page_total": page_total,
        "page": page,
        "page_size": page_size,
    }
