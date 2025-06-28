#!/usr/bin/env python3
"""
添加数据库备份任务脚本
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.deps import SessionLocal
from app.models.job import Job
from app.core.scheduler import add_job_to_scheduler


def add_backup_job():
    """添加数据库备份任务"""
    db = SessionLocal()

    try:
        # 检查是否已存在备份任务
        existing_job = db.query(Job).filter(Job.name == "数据库备份任务").first()
        if existing_job:
            print(f"备份任务已存在，ID: {existing_job.id}")
            return existing_job.id

        # 创建备份任务
        backup_job = Job(
            name="数据库备份任务",
            desc="每1秒备份数据库到data/backups目录，保留最新7份备份",
            trigger_type="interval",
            interval_seconds=1,
            mode="function",
            command="backup_database",
            allow_mode=0,
            max_run_count=0,
            state=1,
        )

        db.add(backup_job)
        db.commit()
        db.refresh(backup_job)

        # 添加到调度器
        add_job_to_scheduler(backup_job)

        print(f"数据库备份任务创建成功，ID: {backup_job.id}")
        print(f"任务名称: {backup_job.name}")
        print(f"执行模式: {backup_job.mode}")
        print(f"执行命令: {backup_job.command}")
        print(f"cron表达式: {backup_job.cron_expr}")
        print(f"状态: {'运行中' if backup_job.state == 1 else '已停止'}")

        return backup_job.id

    except Exception as e:
        print(f"创建备份任务失败: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def start_backup_job():
    """启动备份任务"""
    db = SessionLocal()

    try:
        backup_job = db.query(Job).filter(Job.name == "数据库备份任务").first()
        if not backup_job:
            print("备份任务不存在，请先创建")
            return False

        backup_job.state = 0  # 设置为停止状态，然后重新添加到调度器
        db.commit()

        # 重新添加到调度器
        add_job_to_scheduler(backup_job)

        print(f"数据库备份任务已启动，ID: {backup_job.id}")
        return True

    except Exception as e:
        print(f"启动备份任务失败: {e}")
        return False
    finally:
        db.close()


def stop_backup_job():
    """停止备份任务"""
    db = SessionLocal()

    try:
        backup_job = db.query(Job).filter(Job.name == "数据库备份任务").first()
        if not backup_job:
            print("备份任务不存在")
            return False

        backup_job.state = 2  # 设置为停止状态
        db.commit()

        print(f"数据库备份任务已停止，ID: {backup_job.id}")
        return True

    except Exception as e:
        print(f"停止备份任务失败: {e}")
        return False
    finally:
        db.close()


def show_backup_job_status():
    """显示备份任务状态"""
    db = SessionLocal()

    try:
        backup_job = db.query(Job).filter(Job.name == "数据库备份任务").first()
        if not backup_job:
            print("备份任务不存在")
            return

        print(f"备份任务状态:")
        print(f"  ID: {backup_job.id}")
        print(f"  名称: {backup_job.name}")
        print(f"  描述: {backup_job.desc}")
        print(f"  执行模式: {backup_job.mode}")
        print(f"  执行命令: {backup_job.command}")
        print(f"  cron表达式: {backup_job.cron_expr}")
        print(
            f"  状态: {'运行中' if backup_job.state == 1 else '已停止' if backup_job.state == 2 else '等待中'}"
        )
        print(f"  已执行次数: {backup_job.run_count}")
        print(
            f"  最大执行次数: {backup_job.max_run_count if backup_job.max_run_count > 0 else '无限制'}"
        )
        print(f"  创建时间: {backup_job.created_at}")
        print(f"  更新时间: {backup_job.updated_at}")

    except Exception as e:
        print(f"获取备份任务状态失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="数据库备份任务管理")
    parser.add_argument(
        "action",
        choices=["create", "start", "stop", "status"],
        help="操作类型: create(创建), start(启动), stop(停止), status(状态)",
    )

    args = parser.parse_args()

    if args.action == "create":
        add_backup_job()
    elif args.action == "start":
        start_backup_job()
    elif args.action == "stop":
        stop_backup_job()
    elif args.action == "status":
        show_backup_job_status()
