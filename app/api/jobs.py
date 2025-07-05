import json
import os
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config import Config
from app.core.scheduler import add_job_to_scheduler, remove_job, run_job, scheduler
from app.deps import get_db
from app.function.registry import hot_reload
from app.middlewares.ip_control import ip_control
from app.models.base import error_response, paginated_response, success_response
from app.models.job import Job
from app.models.schemas import JobCreate, JobResponse, JobUpdate

router = APIRouter(prefix="/jobs", tags=["任务管理"])


# 新增任务
@router.post(
    "/add",
    summary="创建新任务",
    description="创建一个新的定时任务，支持HTTP、命令、函数等多种执行模式",
    response_description="任务创建成功，返回任务ID",
    status_code=200,
)
def add_job(job: JobCreate, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    创建新的定时任务

    - **name**: 任务名称（必填）
    - **cron_expr**: cron表达式（必填，格式：分 时 日 月 周）
    - **mode**: 执行模式（http/command/function/func）
    - **command**: 执行命令或URL（必填）
    - **allow_mode**: 执行模式（0=并发, 1=串行, 2=立即）
    - **max_run_count**: 最大执行次数（0=无限制）
    """
    db_job = Job(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    add_job_to_scheduler(db_job)
    return success_response(data={"id": db_job.id}, msg="任务创建成功")


# 编辑任务
@router.post(
    "/edit",
    summary="更新任务",
    description="更新指定任务的配置信息，支持部分字段更新",
    response_description="任务更新成功",
    status_code=200,
)
def edit_job(
    job: JobUpdate,
    id: int = Query(..., description="任务ID", ge=1),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    更新任务配置

    - **job**: 任务更新数据（请求体）
    - **id**: 任务ID（查询参数）
    """
    db_job = db.query(Job).filter(Job.id == id).first()
    if not db_job:
        return error_response(code=404, msg="任务不存在")
    for k, v in job.model_dump(exclude_unset=True).items():
        setattr(db_job, k, v)
    db.commit()
    db.refresh(db_job)
    add_job_to_scheduler(db_job)
    return success_response(msg="任务更新成功")


# 删除任务
@router.post(
    "/del",
    summary="删除任务",
    description="删除指定的任务，同时会停止该任务的调度",
    response_description="任务删除成功",
    status_code=200,
)
def delete_job(
    id: int = Query(..., description="任务ID", ge=1), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    删除任务

    - **id**: 任务ID（查询参数）
    """
    db_job = db.query(Job).filter(Job.id == id).first()
    if not db_job:
        return error_response(code=404, msg="任务不存在")
    db.delete(db_job)
    db.commit()
    remove_job(id)
    return success_response(msg="任务删除成功")


# 任务列表
@router.get(
    "/list",
    summary="获取任务列表",
    description="分页获取所有任务的列表信息",
    response_description="任务列表和总数",
    status_code=200,
)
def list_jobs(
    page: int = Query(1, description="页码", ge=1),
    size: int = Query(10, description="每页数量", ge=1, le=100),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    获取任务列表

    - **page**: 页码（默认1）
    - **size**: 每页数量（默认10，最大100）
    """
    q = db.query(Job)
    total = q.count()
    jobs = q.offset((page - 1) * size).limit(size).all()

    job_list = [
        {
            "id": j.id,
            "name": j.name,
            "cron_expr": j.cron_expr,
            "mode": j.mode,
            "command": j.command,
            "state": j.state,
        }
        for j in jobs
    ]

    return paginated_response(
        data=job_list, total=total, page=page, page_size=size, msg="获取任务列表成功"
    )


# 任务详情
@router.get(
    "/read",
    summary="获取任务详情",
    description="获取指定任务的详细信息",
    response_description="任务的完整信息",
    status_code=200,
)
def job_detail(
    id: int = Query(..., description="任务ID", ge=1), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取任务详情

    - **id**: 任务ID（查询参数）
    """
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        return error_response(code=404, msg="任务不存在")
    return success_response(data=JobResponse.model_validate(job), msg="获取任务详情成功")


# 手动运行
@router.post(
    "/run",
    summary="手动运行任务",
    description="立即手动触发指定任务的执行",
    response_description="任务已手动触发",
    status_code=200,
)
def run_job_api(
    id: int = Query(..., description="任务ID", ge=1), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    手动运行任务

    - **id**: 任务ID（查询参数）
    """
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        return error_response(code=404, msg="任务不存在")
    run_job(job.id)
    return success_response(msg="任务已手动触发")


# 停止任务
@router.post(
    "/stop",
    summary="停止任务",
    description="停止指定任务的调度和执行",
    response_description="任务已停止",
    status_code=200,
)
def stop_job(
    id: int = Query(..., description="任务ID", ge=1), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    停止任务

    - **id**: 任务ID（查询参数）
    """
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        return error_response(code=404, msg="任务不存在")
    setattr(job, "state", 2)
    db.commit()
    remove_job(id)
    return success_response(msg="任务已停止")


# 重启任务
@router.post(
    "/restart",
    summary="重启任务",
    description="重启指定任务，重新加入调度器，并将状态设为运行中",
    response_description="任务已重启",
    status_code=200,
)
def restart_job(
    id: int = Query(..., description="任务ID", ge=1), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    重启任务

    - **id**: 任务ID（查询参数）
    """
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        return error_response(code=404, msg="任务不存在")
    setattr(job, "state", 1)  # 设为运行中
    db.commit()
    add_job_to_scheduler(job)
    return success_response(msg="任务已重启")


# 批量运行所有任务
@router.post(
    "/runAll",
    summary="批量运行所有任务",
    description="手动触发所有可运行的任务（状态为0或1的任务）",
    response_description="所有任务已手动触发",
    status_code=200,
)
def run_all_jobs(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    批量运行所有任务

    手动触发所有可运行的任务（状态为0或1的任务）
    """
    jobs = db.query(Job).filter(Job.state.in_([0, 1])).all()
    for job in jobs:
        run_job(job.id)
    return success_response(msg="所有任务已手动触发")


# 批量停止所有任务
@router.post(
    "/stopAll",
    summary="批量停止所有任务",
    description="停止所有正在运行或等待中的任务",
    response_description="所有任务已停止",
    status_code=200,
)
def stop_all_jobs(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    批量停止所有任务

    停止所有正在运行或等待中的任务
    """
    jobs = db.query(Job).filter(Job.state.in_([0, 1])).all()
    for job in jobs:
        setattr(job, "state", 2)
        remove_job(job.id)
    db.commit()
    return success_response(msg="所有任务已停止")


# 任务状态
@router.get(
    "/jobState",
    summary="获取任务状态统计",
    description="获取任务总数、运行中、已停止的统计信息",
    response_description="任务状态统计",
    status_code=200,
)
def job_state(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    获取任务状态统计

    获取任务总数、运行中、已停止的统计信息
    """
    total = db.query(Job).count()
    running = db.query(Job).filter(Job.state == 1).count()
    stopped = db.query(Job).filter(Job.state == 2).count()

    return success_response(
        data={"total": total, "running": running, "stopped": stopped},
        msg="获取任务状态统计成功",
    )


# 调度器任务列表
@router.get(
    "/scheduler",
    summary="获取调度器任务",
    description="获取当前调度器中所有任务的列表",
    response_description="调度器任务列表",
    status_code=200,
)
def scheduler_tasks() -> Dict[str, Any]:
    """
    获取调度器任务列表

    返回当前调度器中所有任务的ID和下次运行时间
    """
    jobs = scheduler.get_jobs()
    job_list = [{"id": j.id, "next_run_time": str(j.next_run_time)} for j in jobs]

    return success_response(data=job_list, msg="获取调度器任务成功")


# 任务校准（重新加载所有任务）
@router.post(
    "/checkJob",
    summary="校准任务调度器",
    description="重新启动调度器并重新加载所有任务",
    response_description="任务调度器已校准",
    status_code=200,
)
def calibrate_jobs() -> Dict[str, Any]:
    """
    校准任务调度器

    停止并重新启动调度器，重新加载所有任务
    """
    from app.core.scheduler import start_scheduler, stop_scheduler

    stop_scheduler()
    start_scheduler()
    return success_response(msg="任务调度器已校准并重载所有任务")


# 查询任务日志（分页、可按日期过滤）
@router.post(
    "/logs",
    summary="获取任务执行日志",
    description="获取指定任务的执行日志，支持分页和日期过滤",
    response_description="任务执行日志列表",
    status_code=200,
)
def job_logs(
    id: int = Query(..., description="任务ID", ge=1),
    limit: int = Query(10, description="每页数量", ge=1, le=100),
    page: int = Query(1, description="页码", ge=1),
    date: str = Query("", description="日期过滤（格式：YYYY-MM-DD）"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    获取任务执行日志

    - **id**: 任务ID（必填）
    - **limit**: 每页数量（默认10）
    - **page**: 页码（默认1）
    - **date**: 日期过滤（可选，格式：YYYY-MM-DD）
    """
    # 从文件读取日志
    return get_job_logs_from_file(id, limit, page, date)


def get_job_logs_from_file(
    job_id: int, limit: int, page: int, date: str
) -> Dict[str, Any]:
    """从文件读取任务日志"""
    # 如果date为空，默认当天
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    # 构建日志文件路径，年月合并
    year = date[:4]
    month = date[5:7]
    day = date[8:10]
    year_month = f"{year}{month}"
    log_file = f"runtime/jobs/{job_id}/{year_month}/{day}.log"

    logs = []
    total = 0

    try:
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                total = len(lines)

                # 解析JSON日志
                for line in lines:
                    line = line.strip()
                    if line:
                        try:
                            log_entry = json.loads(line)
                            logs.append(log_entry)
                        except json.JSONDecodeError:
                            continue

                # 按时间倒序排列（最新的在前）
                logs.reverse()

                # 分页处理
                start = (page - 1) * limit
                end = start + limit
                logs = logs[start:end]
        else:
            # 文件不存在，返回空结果
            logs = []
            total = 0

    except Exception as e:
        return error_response(msg=f"读取日志文件失败: {str(e)}", code=500)

    return paginated_response(
        data=logs, total=total, page=page, page_size=limit, msg="获取任务执行日志成功"
    )


# 系统日志（读取最近N行日志文件）
@router.get(
    "/zapLogs",
    summary="获取系统日志",
    description="读取系统日志文件的最新N行",
    response_description="系统日志内容",
    status_code=200,
)
def zap_logs(n: int = Query(100, description="读取行数", ge=1, le=1000)) -> Dict[str, Any]:
    """
    获取系统日志

    - **n**: 读取行数（默认100，最大1000）
    """
    log_path = os.getenv("SYSTEM_LOG_PATH", "./runtime/system.log")
    if not os.path.exists(log_path):
        return error_response(msg="日志文件不存在", code=404)
    lines = []
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f.readlines()[-n:]:
            lines.append(line.rstrip())
    return success_response(data={"lines": lines}, msg="获取系统日志成功")


# 日志开关状态（示例：返回True/False）
@router.get(
    "/switchState",
    summary="获取日志开关状态",
    description="获取系统日志功能的开关状态",
    response_description="日志开关状态",
    status_code=200,
)
def log_switch_state() -> Dict[str, Any]:
    """
    获取日志开关状态

    返回系统日志功能的启用状态
    """
    # 可根据实际日志配置返回
    return success_response(data={"log_enabled": True}, msg="获取日志开关状态成功")


# 系统状态
@router.get(
    "/jobStatus",
    summary="获取系统状态",
    description="获取系统整体状态，包括任务总数、运行中、等待中、已停止的数量",
    response_description="系统状态统计",
    status_code=200,
)
def job_status(db: Session = Depends(get_db)) -> Dict[str, int]:
    """
    获取系统状态

    返回系统整体状态统计信息
    """
    total = db.query(Job).count()
    running = db.query(Job).filter(Job.state == 1).count()
    waiting = db.query(Job).filter(Job.state == 0).count()
    stopped = db.query(Job).filter(Job.state == 2).count()
    return {"total": total, "running": running, "waiting": waiting, "stopped": stopped}


# 获取所有可用函数（示例返回）
@router.get(
    "/functions",
    summary="获取可用函数",
    description="获取系统中所有可用的自定义函数列表",
    response_description="可用函数列表",
    status_code=200,
)
def get_functions() -> List[Dict[str, str]]:
    """
    获取可用函数列表

    返回系统中所有可用的自定义函数
    """
    # 可扩展为动态注册函数
    return [
        {"name": "http_get", "desc": "HTTP GET请求"},
        {"name": "shell_cmd", "desc": "Shell命令执行"},
        {"name": "custom_func", "desc": "自定义Python函数"},
    ]


# 函数热加载
@router.post(
    "/functions/reload",
    summary="重新加载函数",
    description="热加载用户自定义函数目录下的所有函数",
    response_description="函数重新加载完成",
    status_code=200,
)
def reload_functions() -> Dict[str, Any]:
    """
    重新加载函数

    热加载用户自定义函数目录下的所有函数
    """
    func_dir = os.getenv("FUNC_DIR", "./python/pyjobs/app/function/user_funcs")
    hot_reload(func_dir)
    return success_response(msg=f"已热加载目录{func_dir}下所有函数")


# 数据库信息
@router.get(
    "/dbinfo",
    summary="获取数据库信息",
    description="获取当前数据库连接信息",
    response_description="数据库连接信息",
    status_code=200,
)
def db_info() -> Dict[str, str]:
    """
    获取数据库信息

    返回当前数据库连接配置信息
    """
    return {
        "db_type": Config.DATABASE_TYPE,
        "db_url": Config.get_database_url(),
        "table_prefix": (
            Config.DATABASE_SQLITE_TABLEPREFIX
            if Config.DATABASE_TYPE == "sqlite"
            else Config.DATABASE_MYSQL_TABLEPREFIX
        ),
    }


# 重载配置
@router.post(
    "/reload-config",
    summary="重新加载配置",
    description="重新加载系统配置文件",
    response_description="配置重新加载完成",
    status_code=200,
)
def reload_config() -> Dict[str, Any]:
    """
    重新加载配置

    重新加载系统配置文件
    """
    return success_response(msg="配置已热重载")


# IP控制相关API
@router.get(
    "/ip-control/status",
    summary="获取IP控制状态",
    description="获取当前IP白名单和黑名单的状态",
    response_description="IP控制状态信息",
    status_code=200,
)
def ip_control_status() -> Dict[str, Any]:
    """
    获取IP控制状态

    返回当前IP白名单和黑名单的内容
    """
    return {
        "whitelist": list(ip_control.whitelist),
        "blacklist": list(ip_control.blacklist),
    }


@router.post(
    "/ip-control/whitelist/add",
    summary="添加IP到白名单",
    description="将指定IP地址添加到白名单",
    response_description="IP已添加到白名单",
    status_code=200,
)
def add_to_whitelist(
    ip: str = Query(..., description="IP地址", pattern=r"^(\d{1,3}\.){3}\d{1,3}$")
) -> Dict[str, Any]:
    """
    添加IP到白名单

    - **ip**: IP地址（必填，格式：xxx.xxx.xxx.xxx）
    """
    ip_control.add_to_whitelist(ip)
    return success_response(msg=f"{ip} added to whitelist")


@router.post(
    "/ip-control/whitelist/remove",
    summary="从白名单移除IP",
    description="从白名单中移除指定IP地址",
    response_description="IP已从白名单移除",
    status_code=200,
)
def remove_from_whitelist(
    ip: str = Query(..., description="IP地址", pattern=r"^(\d{1,3}\.){3}\d{1,3}$")
) -> Dict[str, Any]:
    """
    从白名单移除IP

    - **ip**: IP地址（必填，格式：xxx.xxx.xxx.xxx）
    """
    ip_control.remove_from_whitelist(ip)
    return success_response(msg=f"{ip} removed from whitelist")


@router.post(
    "/ip-control/blacklist/add",
    summary="添加IP到黑名单",
    description="将指定IP地址添加到黑名单",
    response_description="IP已添加到黑名单",
    status_code=200,
)
def add_to_blacklist(
    ip: str = Query(..., description="IP地址", pattern=r"^(\d{1,3}\.){3}\d{1,3}$")
) -> Dict[str, Any]:
    """
    添加IP到黑名单

    - **ip**: IP地址（必填，格式：xxx.xxx.xxx.xxx）
    """
    ip_control.add_to_blacklist(ip)
    return success_response(msg=f"{ip} added to blacklist")


@router.post(
    "/ip-control/blacklist/remove",
    summary="从黑名单移除IP",
    description="从黑名单中移除指定IP地址",
    response_description="IP已从黑名单移除",
    status_code=200,
)
def remove_from_blacklist(
    ip: str = Query(..., description="IP地址", pattern=r"^(\d{1,3}\.){3}\d{1,3}$")
) -> Dict[str, Any]:
    """
    从黑名单移除IP

    - **ip**: IP地址（必填，格式：xxx.xxx.xxx.xxx）
    """
    ip_control.remove_from_blacklist(ip)
    return success_response(msg=f"{ip} removed from blacklist")
