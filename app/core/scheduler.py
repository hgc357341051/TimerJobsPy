import threading
from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.config import Config
from app.core.runner import run_job
from app.deps import SessionLocal
from app.models.job import Job

scheduler = BackgroundScheduler(
    job_defaults=Config.SCHEDULER_JOB_DEFAULTS,
    max_workers=Config.SCHEDULER_MAX_WORKERS,
)
scheduler_lock = threading.Lock()


def add_job_to_scheduler(job: Job) -> None:
    """添加任务到调度器，支持cron和interval"""
    if (
        getattr(job, "trigger_type", "cron") == "interval"
        and getattr(job, "interval_seconds", 0) > 0
    ):
        trigger = IntervalTrigger(seconds=job.interval_seconds)
    elif getattr(job, "trigger_type", "cron") == "cron":
        cron_parts = job.cron_expr.split()
        print(
            f"[调度器] 收到cron表达式: {job.cron_expr}, "
            f"解析: {cron_parts}, 长度: {len(cron_parts)}"
        )
        if len(cron_parts) == 5:
            # 处理特殊情况：如果日、月、周都是0，则使用默认值
            minute = cron_parts[0]
            hour = cron_parts[1]
            day = cron_parts[2] if cron_parts[2] != "0" else "*"
            month = cron_parts[3] if cron_parts[3] != "0" else "*"
            day_of_week = cron_parts[4] if cron_parts[4] != "0" else "*"
            
            print(
                f"[调度器] 使用5位cron, 参数: minute={minute}, "
                f"hour={hour}, day={day}, "
                f"month={month}, day_of_week={day_of_week}"
            )
            trigger = CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week,
            )
        elif len(cron_parts) == 6:
            print(
                f"[调度器] 使用6位cron, 参数: second={cron_parts[0]}, "
                f"minute={cron_parts[1]}, hour={cron_parts[2]}, "
                f"day={cron_parts[3]}, month={cron_parts[4]}, "
                f"day_of_week={cron_parts[5]}"
            )
            trigger = CronTrigger(
                second=cron_parts[0],
                minute=cron_parts[1],
                hour=cron_parts[2],
                day=cron_parts[3],
                month=cron_parts[4],
                day_of_week=cron_parts[5],
            )
        else:
            print(f"[调度器] 无效的cron表达式: {job.cron_expr}")
            return
    else:
        print("[调度器] 无效的trigger_type或参数")
        return
    try:
        scheduler.add_job(
            run_job, trigger, args=[job.id], id=str(job.id), replace_existing=True
        )
        print(f"任务 {job.name} (ID: {job.id}) 已添加到调度器")
    except Exception as e:
        print(f"添加任务到调度器失败: {e}")


def remove_job(job_id: int) -> None:
    """从调度器移除任务"""
    with scheduler_lock:
        try:
            scheduler.remove_job(str(job_id))
            print(f"任务 {job_id} 已从调度器移除")
        except Exception as e:
            print(f"移除任务失败: {e}")


def start_scheduler() -> None:
    """启动调度器"""
    with scheduler_lock:
        if not scheduler.running:
            scheduler.start()
            print("调度器已启动")

            # 启动时自动加载数据库中所有有效任务
            db = SessionLocal()
            try:
                jobs = db.query(Job).filter(Job.state.in_([0, 1])).all()
                print(f"发现 {len(jobs)} 个有效任务")
                for job in jobs:
                    add_job_to_scheduler(job)
            except Exception as e:
                print(f"加载任务失败: {e}")
            finally:
                db.close()


def stop_scheduler() -> None:
    """停止调度器"""
    with scheduler_lock:
        if scheduler.running:
            scheduler.shutdown(wait=False)
            print("调度器已停止")


def get_scheduler_jobs() -> list[Any]:
    """获取调度器中的所有任务"""
    return list(scheduler.get_jobs())
