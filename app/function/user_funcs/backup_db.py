"""
数据库备份函数
每1秒备份数据库到data/backups目录，保留最新7份备份
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from app.config import Config


def backup_database() -> Dict[str, Any]:
    """
    备份数据库函数

    功能：
    1. 备份当前数据库到data/backups目录
    2. 保留最新7份备份
    3. 删除旧的备份文件

    返回：
    - success: 是否成功
    - message: 操作消息
    - backup_file: 备份文件名
    - backup_count: 当前备份数量
    """
    try:
        # 获取数据库路径
        db_path = Config.get_database_url()
        if db_path.startswith("sqlite:///"):
            db_path = db_path.replace("sqlite:///", "")
        else:
            return {
                "success": False,
                "message": f"不支持的数据库类型: {db_path}",
                "backup_file": None,
                "backup_count": 0,
            }

        # 确保数据库文件存在
        if not os.path.exists(db_path):
            return {
                "success": False,
                "message": f"数据库文件不存在: {db_path}",
                "backup_file": None,
                "backup_count": 0,
            }

        # 创建备份目录
        backup_dir = Path(Config.BACKUP_DIR)
        backup_dir.mkdir(parents=True, exist_ok=True)

        # 生成备份文件名（包含时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"xiaohu_jobs_backup_{timestamp}.db"
        backup_path = backup_dir / backup_filename

        # 执行备份
        shutil.copy2(db_path, backup_path)

        # 获取所有备份文件
        backup_files = list(backup_dir.glob("xiaohu_jobs_backup_*.db"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        # 保留最新7份，删除多余的
        max_backups = Config.JOB_LOG_KEEP_COUNT
        if len(backup_files) > max_backups:
            for old_backup in backup_files[max_backups:]:
                try:
                    os.remove(old_backup)
                except Exception as e:
                    print(f"删除旧备份文件失败: {old_backup}, 错误: {e}")

        # 获取备份文件大小
        backup_size = os.path.getsize(backup_path)
        backup_size_mb = round(backup_size / (1024 * 1024), 2)

        return {
            "success": True,
            "message": "数据库备份成功",
            "backup_file": backup_filename,
            "backup_path": str(backup_path),
            "backup_size_mb": backup_size_mb,
            "backup_count": len(backup_files),
            "timestamp": timestamp,
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"数据库备份失败: {str(e)}",
            "backup_file": None,
            "backup_count": 0,
        }


def get_backup_status() -> Dict[str, Any]:
    """
    获取备份状态函数

    返回：
    - backup_count: 当前备份数量
    - backup_files: 备份文件列表
    - total_size_mb: 总备份大小
    """
    try:
        backup_dir = Path(Config.BACKUP_DIR)
        if not backup_dir.exists():
            return {"backup_count": 0, "backup_files": [], "total_size_mb": 0}

        backup_files = list(backup_dir.glob("xiaohu_jobs_backup_*.db"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        total_size = sum(f.stat().st_size for f in backup_files)
        total_size_mb = round(total_size / (1024 * 1024), 2)

        file_list = []
        for f in backup_files:
            file_list.append(
                {
                    "filename": f.name,
                    "size_mb": round(f.stat().st_size / (1024 * 1024), 2),
                    "modified_time": datetime.fromtimestamp(f.stat().st_mtime).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }
            )

        return {
            "backup_count": len(backup_files),
            "backup_files": file_list,
            "total_size_mb": total_size_mb,
        }

    except Exception as e:
        return {
            "backup_count": 0,
            "backup_files": [],
            "total_size_mb": 0,
            "error": str(e),
        }


def cleanup_backups() -> Dict[str, Any]:
    """
    清理备份函数

    删除所有备份文件，只保留最新7份
    """
    try:
        backup_dir = Path(Config.BACKUP_DIR)
        if not backup_dir.exists():
            return {
                "success": True,
                "message": "备份目录不存在，无需清理",
                "deleted_count": 0,
            }

        backup_files = list(backup_dir.glob("xiaohu_jobs_backup_*.db"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        max_backups = Config.JOB_LOG_KEEP_COUNT
        deleted_count = 0

        if len(backup_files) > max_backups:
            for old_backup in backup_files[max_backups:]:
                try:
                    os.remove(old_backup)
                    deleted_count += 1
                except Exception as e:
                    print(f"删除旧备份文件失败: {old_backup}, 错误: {e}")

        return {
            "success": True,
            "message": f"清理完成，删除了 {deleted_count} 个旧备份文件",
            "deleted_count": deleted_count,
            "remaining_count": len(backup_files) - deleted_count,
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"清理备份失败: {str(e)}",
            "deleted_count": 0,
        }
