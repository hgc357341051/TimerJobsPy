#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库备份函数
"""

import os
import shutil
import sqlite3
from datetime import datetime


def backup_database() -> dict:
    """
    备份数据库文件

    将当前的数据库文件备份到backup目录，文件名包含时间戳
    """
    try:
        # 数据库文件路径
        db_path = "data/jobs.db"
        backup_dir = "data/backups"

        # 检查数据库文件是否存在
        if not os.path.exists(db_path):
            return {
                "success": False,
                "message": f"数据库文件不存在: {db_path}",
                "backup_path": None,
            }

        # 创建备份目录
        os.makedirs(backup_dir, exist_ok=True)

        # 生成备份文件名（包含时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"jobs_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)

        # 复制数据库文件
        shutil.copy2(db_path, backup_path)

        # 验证备份文件
        if os.path.exists(backup_path):
            # 检查备份文件是否可读
            try:
                conn = sqlite3.connect(backup_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                conn.close()

                return {
                    "success": True,
                    "message": "数据库备份成功",
                    "backup_path": backup_path,
                    "backup_size": os.path.getsize(backup_path),
                    "table_count": table_count,
                    "timestamp": timestamp,
                }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"备份文件验证失败: {str(e)}",
                    "backup_path": backup_path,
                }
        else:
            return {"success": False, "message": "备份文件创建失败", "backup_path": None}

    except Exception as e:
        return {
            "success": False,
            "message": f"备份过程中发生错误: {str(e)}",
            "backup_path": None,
        }


def cleanup_old_backups(keep_count: int = 10) -> dict:
    """
    清理旧的备份文件，只保留最新的几个

    Args:
        keep_count: 保留的备份文件数量，默认10个
    """
    try:
        backup_dir = "data/backups"

        if not os.path.exists(backup_dir):
            return {"success": False, "message": f"备份目录不存在: {backup_dir}"}

        # 获取所有备份文件
        backup_files = []
        for file in os.listdir(backup_dir):
            if file.startswith("jobs_backup_") and file.endswith(".db"):
                file_path = os.path.join(backup_dir, file)
                backup_files.append((file_path, os.path.getmtime(file_path)))

        # 按修改时间排序
        backup_files.sort(key=lambda x: x[1], reverse=True)

        # 删除多余的备份文件
        deleted_count = 0
        for file_path, _ in backup_files[keep_count:]:
            try:
                os.remove(file_path)
                deleted_count += 1
            except Exception as e:
                print(f"删除备份文件失败 {file_path}: {e}")

        return {
            "success": True,
            "message": f"清理完成，删除了 {deleted_count} 个旧备份文件",
            "deleted_count": deleted_count,
            "remaining_count": len(backup_files) - deleted_count,
        }

    except Exception as e:
        return {"success": False, "message": f"清理过程中发生错误: {str(e)}"}


def backup_and_cleanup() -> dict:
    """
    执行备份并清理旧文件
    """
    # 先执行备份
    backup_result = backup_database()

    # 再清理旧备份
    cleanup_result = cleanup_old_backups()

    return {
        "backup": backup_result,
        "cleanup": cleanup_result,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
