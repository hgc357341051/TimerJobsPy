#!/usr/bin/env python3
"""
调试调度器脚本
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.deps import SessionLocal
from app.models.job import Job
from app.core.scheduler import scheduler, get_scheduler_jobs, add_job_to_scheduler
from app.function.registry import get_function


def check_scheduler_status():
    """检查调度器状态"""
    print("=== 调度器状态 ===")
    print(f"调度器运行状态: {scheduler.running}")
    print(f"调度器任务数量: {len(scheduler.get_jobs())}")

    if scheduler.running:
        print("调度器正在运行")
    else:
        print("调度器未运行")


def check_database_jobs():
    """检查数据库中的任务"""
    print("\n=== 数据库任务 ===")
    db = SessionLocal()

    try:
        jobs = db.query(Job).all()
        print(f"数据库中共有 {len(jobs)} 个任务")

        for job in jobs:
            print(f"任务ID: {job.id}")
            print(f"  名称: {job.name}")
            print(
                f"  状态: {job.state} ({'运行中' if job.state == 1 else '已停止' if job.state == 2 else '等待中'})"
            )
            print(f"  cron表达式: {job.cron_expr}")
            print(f"  执行模式: {job.mode}")
            print(f"  执行命令: {job.command}")
            print(f"  已执行次数: {job.run_count}")
            print()

    except Exception as e:
        print(f"查询数据库失败: {e}")
    finally:
        db.close()


def check_scheduler_jobs():
    """检查调度器中的任务"""
    print("=== 调度器任务 ===")
    jobs = get_scheduler_jobs()

    if not jobs:
        print("调度器中没有任务")
        return

    for job in jobs:
        print(f"任务ID: {job.id}")
        print(f"  名称: {job.name}")
        print(f"  下次执行时间: {job.next_run_time}")
        print(f"  触发器: {job.trigger}")
        print()


def check_function_registry():
    """检查函数注册表"""
    print("=== 函数注册表 ===")
    try:
        backup_func = get_function("backup_database")
        if backup_func:
            print("backup_database 函数已注册")
            print(f"函数对象: {backup_func}")
        else:
            print("backup_database 函数未注册")
    except Exception as e:
        print(f"检查函数注册失败: {e}")


def reload_backup_job():
    """重新加载备份任务"""
    print("\n=== 重新加载备份任务 ===")
    db = SessionLocal()

    try:
        backup_job = db.query(Job).filter(Job.name == "数据库备份任务").first()
        if not backup_job:
            print("备份任务不存在")
            return

        # 设置状态为运行中
        backup_job.state = 1
        db.commit()

        # 重新添加到调度器
        add_job_to_scheduler(backup_job)

        print(f"备份任务已重新加载，ID: {backup_job.id}")

    except Exception as e:
        print(f"重新加载备份任务失败: {e}")
        db.rollback()
    finally:
        db.close()


def test_backup_function():
    """测试备份函数"""
    print("\n=== 测试备份函数 ===")
    try:
        from app.function.user_funcs.backup_db import backup_database

        result = backup_database()
        print(f"备份结果: {result}")

    except Exception as e:
        print(f"测试备份函数失败: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="调试调度器")
    parser.add_argument(
        "action",
        choices=["status", "db", "scheduler", "function", "reload", "test", "all"],
        help="操作类型",
    )

    args = parser.parse_args()

    if args.action == "status":
        check_scheduler_status()
    elif args.action == "db":
        check_database_jobs()
    elif args.action == "scheduler":
        check_scheduler_jobs()
    elif args.action == "function":
        check_function_registry()
    elif args.action == "reload":
        reload_backup_job()
    elif args.action == "test":
        test_backup_function()
    elif args.action == "all":
        check_scheduler_status()
        check_database_jobs()
        check_scheduler_jobs()
        check_function_registry()
        test_backup_function()
