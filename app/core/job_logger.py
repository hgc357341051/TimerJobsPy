import json
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class JobLogger:
    """任务日志管理器 - 按照 runtime/jobs/任务id/年月/日.log 格式安全写入"""

    def __init__(self, job_id: int, job_name: str):
        self.job_id = job_id
        self.job_name = job_name
        self._file_handles: Dict[str, Any] = {}
        self._file_mutex = threading.RLock()
        self._write_mutex = threading.Lock()

    def _get_log_path(self) -> str:
        """获取日志文件路径"""
        now = datetime.now()
        year_month = f"{now.year}{now.month:02d}"  # 年月合并，如202506
        day = f"{now.day:02d}"

        # 创建目录结构: runtime/jobs/任务ID/年月/日.log
        log_dir = Path("runtime") / "jobs" / str(self.job_id) / year_month

        # 确保目录存在
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"创建日志目录失败: {e}")
            return ""

        return str(log_dir / f"{day}.log")

    def _get_file_handle(self, log_path: str) -> Any:
        """获取文件句柄（带缓存）"""
        # 先尝试从缓存获取
        with self._file_mutex:
            if log_path in self._file_handles:
                return self._file_handles[log_path]

            # 缓存中没有，创建新文件句柄
            try:
                file_handle = open(log_path, "a", encoding="utf-8", buffering=1)
                self._file_handles[log_path] = file_handle
                return file_handle
            except Exception as e:
                print(f"打开日志文件失败: {e}")
                return None

    def _write_log(self, level: str, message: str) -> None:
        """写入日志（单行结构化JSON格式）"""
        log_path = self._get_log_path()
        if not log_path:
            return

        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # 日志级别中文映射
        level_cn_map = {
            "START": "开始",
            "END": "结束",
            "COMMAND": "命令",
            "HTTP": "HTTP",
            "FUNCTION": "函数",
            "ERROR": "错误",
            "SUCCESS": "成功",
            "WARNING": "警告",
        }
        level_cn = level_cn_map.get(level, level)

        log_entry = {
            "time": timestamp,
            "level": level_cn,
            "job_id": self.job_id,
            "job_name": self.job_name,
            "message": message,
        }

        try:
            log_line = json.dumps(log_entry, ensure_ascii=False) + "\n"
        except Exception as e:
            print(f"序列化日志数据失败: {e}")
            return

        # 获取文件句柄
        file_handle = self._get_file_handle(log_path)
        if not file_handle:
            return

        # 使用互斥锁确保写入原子性
        with self._write_mutex:
            try:
                file_handle.write(log_line)
                file_handle.flush()
                os.fsync(file_handle.fileno())  # 同步到磁盘
            except Exception as e:
                print(f"写入日志文件失败: {e}")

    def error(self, message: str) -> None:
        """记录错误日志"""
        self._write_log("ERROR", message)

    def success(self, message: str) -> None:
        """记录成功日志"""
        self._write_log("SUCCESS", message)

    def warning(self, message: str) -> None:
        """记录警告日志"""
        self._write_log("WARNING", message)

    def start(self, mode: str) -> None:
        """记录任务开始日志"""
        message = f"任务开始执行 - 模式: {mode}"
        self._write_log("START", message)

    def end(self, success: bool, duration: float, output: str = "") -> None:
        """记录任务结束日志"""
        status = "成功" if success else "失败"
        message = f"执行状态: {status} | 执行时长: {duration:.3f}秒"
        if output:
            message += f" | 输出: {output}"
        self._write_log("END", message)

    def command_output(
        self, command: str, exit_code: int, stdout: str, stderr: str, duration: float
    ) -> None:
        """记录命令执行输出"""
        details = [
            f"命令: {command}",
            f"退出码: {exit_code}",
            f"执行时长: {duration:.3f}秒",
        ]

        if stdout:
            details.append(f"标准输出:\n{stdout}")

        if stderr:
            details.append(f"错误输出:\n{stderr}")

        message = " | ".join(details)
        self._write_log("COMMAND", message)

    def http_output(
        self,
        url: str,
        method: str,
        status_code: int,
        response_body: str,
        duration: float,
    ) -> None:
        """记录HTTP请求输出"""
        details = [
            f"URL: {url}",
            f"方法: {method}",
            f"状态码: {status_code}",
            f"请求时长: {duration:.3f}秒",
        ]

        if response_body:
            # 限制响应体长度
            if len(response_body) > 1000:
                response_body = response_body[:1000] + "\n... (响应体已截断)"
            details.append(f"响应内容:\n{response_body}")

        message = " | ".join(details)
        self._write_log("HTTP", message)

    def function_output(
        self, function_name: str, args: list, result: str, duration: float
    ) -> None:
        """记录函数执行输出"""
        details = [
            f"函数名: {function_name}",
            f"参数: {args}",
            f"执行时长: {duration:.3f}秒",
        ]

        if result:
            # 限制结果长度
            if len(result) > 1000:
                result = result[:1000] + "\n... (结果已截断)"
            details.append(f"执行结果:\n{result}")

        message = " | ".join(details)
        self._write_log("FUNCTION", message)

    def write_summary_log(self, log_data: Dict[str, Any]) -> None:
        """写入聚合日志"""
        log_path = self._get_log_path()
        if not log_path:
            return

        try:
            log_line = json.dumps(log_data, ensure_ascii=False) + "\n"
        except Exception as e:
            print(f"序列化日志数据失败: {e}")
            return

        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(log_line)
                f.flush()
                os.fsync(f.fileno())
        except Exception as e:
            print(f"写入聚合日志失败: {e}")

    def write_text_log(self, log_data: Dict[str, Any]) -> None:
        """写入JSON格式聚合日志，便于结构化查询"""
        log_path = self._get_log_path()
        if not log_path:
            return

        # 构建JSON日志数据
        json_log = {
            "time": log_data.get("time")
            or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "job_id": log_data.get("job_id", ""),
            "job_name": log_data.get("job_name", ""),
            "status": log_data.get("status", ""),
            "duration_ms": log_data.get("duration_ms", 0),
            "mode": log_data.get("mode", ""),
            "command": log_data.get("command", ""),
            "output": log_data.get("stdout", "")
            or log_data.get("func_result", "")
            or log_data.get("http_resp", ""),
            "error_msg": log_data.get("error_msg", ""),
            "exit_code": log_data.get("exit_code", 0),
            "http_status": log_data.get("http_status", 0),
            "func_name": log_data.get("func_name", ""),
            "func_args": log_data.get("func_args", ""),
        }

        # 写入JSON格式日志
        try:
            log_line = json.dumps(json_log, ensure_ascii=False) + "\n"
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(log_line)
                f.flush()
                os.fsync(f.fileno())
        except Exception as e:
            print(f"写入JSON日志失败: {e}")

    def close_all_handles(self) -> None:
        """关闭所有文件句柄"""
        with self._file_mutex:
            for path, file_handle in self._file_handles.items():
                try:
                    file_handle.close()
                except Exception as e:
                    print(f"关闭文件句柄失败 {path}: {e}")
            self._file_handles.clear()


# 全局文件句柄管理器
_file_handles: Dict[str, Any] = {}
_file_mutex = threading.RLock()


def close_all_job_loggers() -> None:
    """关闭所有任务日志文件句柄（程序退出时调用）"""
    with _file_mutex:
        for path, file_handle in _file_handles.items():
            try:
                file_handle.close()
            except Exception as e:
                print(f"关闭文件句柄失败 {path}: {e}")
        _file_handles.clear()
