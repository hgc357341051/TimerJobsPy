import logging
import subprocess
import time
from datetime import datetime
from typing import Any, Dict

import requests
from app.core.job_logger import JobLogger
from app.deps import SessionLocal
from app.function.registry import get_function, FUNC_REGISTRY
from app.models.job import Job

logger = logging.getLogger(__name__)


def run_job(job_id: int) -> None:
    """执行任务"""
    db = SessionLocal()
    log_detail = {}
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(f"任务 {job_id} 不存在")
            return
        # 检查任务状态
        if job.state != 1:
            logger.info(f"任务 {job_id} 状态为 {job.state}，跳过执行")
            return

        # 检查执行次数限制
        if job.max_run_count > 0 and job.run_count >= job.max_run_count:
            logger.info(f"任务 {job_id} 已达到最大执行次数 {job.max_run_count}")
            return

        # 创建任务日志管理器
        job_logger = JobLogger(job_id=job.id, job_name=job.name)

        start_time = time.time()
        success = False
        error_msg = None

        try:
            if job.mode == "function":
                log_detail = run_function_job(job, job_logger)
            elif job.mode == "http":
                log_detail = run_http_job(job, job_logger)
            else:
                log_detail = {"result": run_command_job(job, job_logger)}
            success = True
            logger.info(f"任务 {job_id} 执行成功")

        except Exception as e:
            error_msg = str(e)
            logger.error(f"任务 {job_id} 执行失败: {e}")

        finally:
            end_time = time.time()
            duration = end_time - start_time

            summary_log = {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "job_id": job.id,
                "job_name": job.name,
                "status": "成功" if success else "失败",
                "duration_ms": int(duration * 1000),
                "mode": job.mode,
                "command": job.command,
                "error_msg": error_msg,
            }
            # 合并详细信息（包含result字段）
            if log_detail and isinstance(log_detail, dict):
                summary_log.update(log_detail)
            job_logger.write_text_log(summary_log)

            # 更新任务执行次数
            job.run_count += 1
            db.commit()

            # 关闭日志文件句柄
            job_logger.close_all_handles()

    except Exception as e:
        logger.error(f"执行任务 {job_id} 时发生错误: {e}")
    finally:
        db.close()


def run_command_job(job: Job, job_logger: JobLogger) -> str:
    """执行命令任务"""
    start_time = time.time()
    try:
        config = parse_command_config(job.command)
        command = config.get("command", "")
        timeout = config.get("timeout", 60)
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )
        end_time = time.time()
        duration = end_time - start_time
        if result.returncode != 0:
            raise Exception(
                f"命令执行失败，退出码: {result.returncode}, 错误: {result.stderr}"
            )
        return result.stdout.strip() if result.stdout else f"exit_code={result.returncode}"
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        raise Exception(f"命令执行超时，超时时间: {timeout}秒")
    except Exception as e:
        duration = time.time() - start_time
        raise


def run_http_job(job: Job, job_logger: JobLogger) -> dict:
    """执行HTTP任务"""
    start_time = time.time()
    try:
        config = parse_http_config(job.command)
        url = config.get("url", "")
        method = config.get("method", "GET")
        timeout = config.get("timeout", 60)
        headers = config.get("headers", {})
        proxy = config.get("proxy", None)
        proxies = None
        proxy_used = None
        if proxy:
            if proxy.startswith("socks5://") or proxy.startswith("socks5h://"):
                proxies = {
                    "http": proxy,
                    "https": proxy
                }
                proxy_used = proxy
            elif proxy.startswith("http://") or proxy.startswith("https://"):
                proxies = {
                    "http": proxy,
                    "https": proxy
                }
                proxy_used = proxy
        try:
            response = requests.request(
                method=method, url=url, headers=headers, timeout=timeout, proxies=proxies
            )
            status_code = response.status_code
            resp_text = response.text.strip()
            success = status_code < 400 and resp_text != ''
        except Exception as e:
            status_code = None
            resp_text = str(e)
            success = False
        end_time = time.time()
        duration = end_time - start_time
        # 格式化result为纯文本
        result_lines = [
            f"url: {url}",
            f"proxy: {proxy_used or 'none'}",
            f"method: {method}",
            f"response: {resp_text}",
            f"status_code: {status_code}",
            f"success: {success}",
            f"duration: {round(duration, 3)}s"
        ]
        result_text = "\n".join(result_lines)
        return {
            "url": url,
            "proxy": proxy_used,
            "method": method,
            "response": resp_text,
            "status_code": status_code,
            "success": success,
            "http_duration": round(duration, 3),
            "result": result_text
        }
    except Exception as e:
        duration = time.time() - start_time
        result_lines = [
            f"url: {url}",
            f"proxy: {proxy_used or 'none'}",
            f"method: {method}",
            f"response: {str(e)}",
            f"status_code: none",
            f"success: false",
            f"duration: {round(duration, 3)}s"
        ]
        result_text = "\n".join(result_lines)
        return {
            "url": url,
            "proxy": proxy_used,
            "method": method,
            "response": str(e),
            "status_code": None,
            "success": False,
            "http_duration": round(duration, 3),
            "result": result_text
        }


def run_function_job(job: Job, job_logger: JobLogger) -> dict:
    """执行函数任务"""
    start_time = time.time()
    try:
        config = parse_function_config(job.command)
        func_name = config.get("name", "")
        args = config.get("args", [])
        func = get_function(func_name)
        if not func:
            raise Exception(f"函数 {func_name} 不存在")
        result = func(*args)
        end_time = time.time()
        duration = end_time - start_time
        # 格式化result为纯文本
        import json as _json
        try:
            result_text = _json.dumps(result, ensure_ascii=False)
        except Exception:
            result_text = str(result)
        return {
            "func_name": func_name,
            "func_args": args,
            "func_duration": round(duration, 3),
            "result": result_text
        }
    except Exception as e:
        duration = time.time() - start_time
        raise


def parse_command_config(command: str) -> Dict[str, Any]:
    """解析命令配置"""
    config: Dict[str, Any] = {"command": command, "timeout": 60}

    lines = command.split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("【timeout】"):
            try:
                config["timeout"] = int(line.split("【timeout】")[1].strip())
            except (ValueError, IndexError):
                pass
        elif line.startswith("【command】"):
            config["command"] = line.split("【command】")[1].strip()

    return config


def parse_http_config(command: str) -> Dict[str, Any]:
    """解析HTTP配置"""
    config: Dict[str, Any] = {
        "url": command,
        "method": "GET",
        "timeout": 60,
        "headers": {},
        "proxy": None,
    }

    lines = command.split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("【url】"):
            config["url"] = line.split("【url】")[1].strip()
        elif line.startswith("【method】"):
            config["method"] = line.split("【method】")[1].strip().upper()
        elif line.startswith("【timeout】"):
            try:
                config["timeout"] = int(line.split("【timeout】")[1].strip())
            except (ValueError, IndexError):
                pass
        elif line.startswith("【header】"):
            header_line = line.split("【header】")[1].strip()
            if ":" in header_line:
                key, value = header_line.split(":", 1)
                config["headers"][key.strip()] = value.strip()
        elif line.startswith("【proxy】"):
            config["proxy"] = line.split("【proxy】")[1].strip()

    return config


def parse_function_config(command: str) -> Dict[str, Any]:
    """解析函数配置"""
    config: Dict[str, Any] = {"name": "", "args": []}

    lines = command.split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("【name】"):
            config["name"] = line.split("【name】")[1].strip()
        elif line.startswith("【arg】"):
            arg_str = line.split("【arg】")[1].strip()
            if arg_str:
                config["args"] = [arg.strip() for arg in arg_str.split(",")]

    # 如果没有【name】，直接用 command 本身作为函数名
    if config["name"] == "" and len(lines) == 1 and lines[0].strip():
        config["name"] = lines[0].strip()
    return config
