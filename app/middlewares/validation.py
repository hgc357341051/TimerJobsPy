"""
Pydantic 中文化异常处理器
将 Pydantic 的英文错误提示转换为中文
"""

import json
import re
from typing import Any, Dict, List, Optional, Sequence

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

# 英文错误信息到中文的映射
ERROR_MESSAGES_ZH = {
    # 基础类型错误
    "field required": "字段必填",
    "field required (type=value_error.missing)": "字段必填",
    "value is not a valid integer": "不是有效的整数",
    "value is not a valid float": "不是有效的浮点数",
    "value is not a valid boolean": "不是有效的布尔值",
    "value is not a valid string": "不是有效的字符串",
    "value is not a valid date": "不是有效的日期",
    "value is not a valid datetime": "不是有效的日期时间",
    "value is not a valid time": "不是有效的时间",
    "value is not a valid uuid": "不是有效的UUID",
    "value is not a valid email": "不是有效的邮箱地址",
    "value is not a valid url": "不是有效的URL",
    "value is not a valid ip address": "不是有效的IP地址",
    # 长度限制
    "ensure this value has at least {limit_value} characters": "长度至少需要{limit_value}个字符",
    "ensure this value has at most {limit_value} characters": "长度不能超过{limit_value}个字符",
    "ensure this value has at least {limit_value} items": "至少需要{limit_value}个项目",
    "ensure this value has at most {limit_value} items": "不能超过{limit_value}个项目",
    # 数值范围
    "ensure this value is greater than {limit_value}": "值必须大于{limit_value}",
    "ensure this value is greater than or equal to {limit_value}": "值必须大于等于{limit_value}",
    "ensure this value is less than {limit_value}": "值必须小于{limit_value}",
    "ensure this value is less than or equal to {limit_value}": "值必须小于等于{limit_value}",
    # 枚举值
    "value is not a valid enumeration member": "不是有效的枚举值",
    "unexpected value": "意外的值",
    # 正则表达式
    "string does not match regex": "字符串格式不正确",
    "string does not match regex '{regex}'": "字符串格式不正确",
    # 自定义错误
    "invalid job mode": "无效的任务执行模式",
    "invalid cron expression": "无效的cron表达式",
    "invalid allow_mode": "无效的执行模式",
    "invalid state": "无效的状态值",
    # 默认错误
    "validation error": "数据验证失败",
    "type_error": "类型错误",
    "value_error": "值错误",
}


def translate_error_message(msg: str, ctx: Optional[Dict[str, Any]] = None) -> str:
    """
    翻译错误信息为中文
    """
    # 处理带参数的错误信息
    if "limit_value" in msg and ctx and "limit_value" in ctx:
        limit_value = ctx["limit_value"]
        msg = msg.replace("{limit_value}", str(limit_value))

    # 查找中文翻译
    for en_msg, zh_msg in ERROR_MESSAGES_ZH.items():
        if en_msg in msg:
            return zh_msg

    # 如果没有找到翻译，返回原信息
    return msg


def format_validation_errors(errors: Sequence[Any]) -> List[Dict[str, Any]]:
    """
    格式化验证错误信息
    """
    formatted_errors = []

    for error in errors:
        # 获取字段路径
        loc = error.get("loc", [])
        field_path = " -> ".join(str(location) for location in loc)

        # 翻译错误信息
        original_msg = error.get("msg", "")
        ctx = error.get("ctx", {})
        translated_msg = translate_error_message(original_msg, ctx)

        # 构建错误信息
        formatted_error = {
            "field": field_path,
            "message": translated_msg,
            "type": error.get("type", "validation_error"),
            "original_message": original_msg,  # 保留原信息用于调试
        }

        formatted_errors.append(formatted_error)
    return formatted_errors


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    FastAPI 请求验证异常处理器
    """
    errors: List[Dict[str, Any]] = format_validation_errors(exc.errors())

    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": "参数验证失败",
            "errors": errors,
            "request_id": getattr(request.state, "request_id", None),
        },
    )


async def pydantic_validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """
    Pydantic 验证异常处理器
    """
    errors: List[Dict[str, Any]] = format_validation_errors(exc.errors())

    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": "数据验证失败",
            "errors": errors,
            "request_id": getattr(request.state, "request_id", None),
        },
    )


def register_validation_handlers(app: FastAPI) -> None:
    """
    注册验证异常处理器
    """
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
    app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)  # type: ignore


async def validate_json_body(request: Request) -> Any:
    """验证JSON请求体"""
    try:
        return await request.json()
    except json.JSONDecodeError:
        raise HTTPException(400, "无效的JSON格式")


def validate_required_fields(data: Dict[str, Any], required_fields: list[str]) -> None:
    """验证必需字段"""
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise HTTPException(400, f"缺少必需字段: {', '.join(missing_fields)}")


def validate_field_type(data: Dict[str, Any], field: str, expected_type: type) -> None:
    """验证字段类型"""
    if field in data and not isinstance(data[field], expected_type):
        raise HTTPException(
            400, f"字段 {field} 类型错误，期望 {expected_type.__name__}"
        )


def validate_string_length(data: Dict[str, Any], field: str, max_length: int) -> None:
    """验证字符串长度"""
    if field in data and isinstance(data[field], str) and len(data[field]) > max_length:
        raise HTTPException(400, f"字段 {field} 长度超过限制 ({max_length})")


def validate_regex_pattern(data: Dict[str, Any], field: str, pattern: str) -> None:
    """验证正则表达式模式"""
    if field in data and isinstance(data[field], str):
        if not re.match(pattern, data[field]):
            raise HTTPException(400, f"字段 {field} 格式不正确")


def validate_enum_value(
    data: Dict[str, Any], field: str, allowed_values: list[str]
) -> None:
    """验证枚举值"""
    if field in data and data[field] not in allowed_values:
        raise HTTPException(
            400, f"字段 {field} 值无效，允许的值: {', '.join(allowed_values)}"
        )


def validate_cron_expression(cron_expr: str) -> None:
    """验证cron表达式"""
    if not cron_expr:
        raise HTTPException(400, "cron表达式不能为空")

    parts = cron_expr.split()
    if len(parts) not in [5, 6]:
        raise HTTPException(400, "cron表达式格式错误，应为5位或6位")

    # 简单的格式验证
    for part in parts:
        if not re.match(r"^[\d*/,\-]+$", part):
            raise HTTPException(400, f"cron表达式包含无效字符: {part}")


def validate_interval_seconds(seconds: int) -> None:
    """验证间隔秒数"""
    if seconds <= 0:
        raise HTTPException(400, "间隔秒数必须大于0")


def validate_job_state(state: int) -> None:
    """验证任务状态"""
    if state not in [0, 1, 2]:
        raise HTTPException(400, "任务状态值无效，应为0(等待)、1(运行)、2(停止)")


def validate_trigger_type(trigger_type: str) -> None:
    """验证触发器类型"""
    if trigger_type not in ["cron", "interval"]:
        raise HTTPException(400, "触发器类型无效，应为cron或interval")
