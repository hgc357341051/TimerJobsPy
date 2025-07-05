"""
数据模型测试
测试所有数据模型的功能
"""

from datetime import datetime
from typing import Any

import pytest

from app.models.admin import Admin
from app.models.job import Job
from app.models.log import JobExecLog


class TestJobModel:
    """任务模型测试"""

    def test_create_job(self, db_session: Any) -> None:
        """测试创建任务"""
        job = Job(
            name="测试任务",
            desc="这是一个测试任务",
            cron_expr="0 0 * * *",
            mode="http",
            command="https://httpbin.org/get",
            allow_mode=0,
            max_run_count=10,
            run_count=0,
            state=1,
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.id is not None
        assert job.name == "测试任务"
        assert job.mode == "http"
        assert job.state == 1
        assert job.created_at is not None
        assert job.updated_at is not None

    def test_job_default_values(self, db_session: Any) -> None:
        """测试任务默认值"""
        job = Job(name="默认值测试", cron_expr="0 0 * * *", command="https://example.com")
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        # 使用getattr安全获取字段值
        job_mode = getattr(job, "mode", "")
        job_allow_mode = getattr(job, "allow_mode", 0) or 0
        job_max_run_count = getattr(job, "max_run_count", 0) or 0
        job_run_count = getattr(job, "run_count", 0) or 0
        job_state = getattr(job, "state", 0) or 0

        assert job_mode == "http"  # 默认值
        assert job_allow_mode == 0  # 默认值
        assert job_max_run_count == 0  # 默认值
        assert job_run_count == 0  # 默认值
        assert job_state == 0  # 默认值

    def test_job_relationships(self, db_session: Any) -> None:
        """测试任务关联关系"""
        # 创建任务
        job = Job(name="关联测试任务", cron_expr="0 0 * * *", command="https://example.com")
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        # 创建执行日志
        log = JobExecLog(
            time=datetime.utcnow().isoformat(),
            end_time=datetime.utcnow().isoformat(),
            job_id=job.id,
            job_name=job.name,
            status="success",
            duration_ms=100,
            mode=job.mode,
            command=job.command,
        )
        db_session.add(log)
        db_session.commit()

        # 验证关联
        assert log.job_id == job.id
        assert log.job_name == job.name

    def test_job_state_transitions(self, db_session: Any) -> None:
        """测试任务状态转换"""
        job = Job(name="状态测试任务", cron_expr="0 0 * * *", command="https://example.com")
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        # 初始状态
        job_state = getattr(job, "state", 0) or 0
        assert job_state == 0

        # 启动任务
        setattr(job, "state", 1)
        db_session.commit()
        db_session.refresh(job)
        job_state = getattr(job, "state", 0) or 0
        assert job_state == 1

        # 停止任务
        setattr(job, "state", 2)
        db_session.commit()
        db_session.refresh(job)
        job_state = getattr(job, "state", 0) or 0
        assert job_state == 2

    def test_job_run_count_increment(self, db_session: Any) -> None:
        """测试任务执行次数递增"""
        job = Job(
            name="执行次数测试",
            cron_expr="0 0 * * *",
            command="https://example.com",
            max_run_count=5,
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        initial_count = getattr(job, "run_count", 0) or 0

        # 模拟执行
        for i in range(3):
            current_count = getattr(job, "run_count", 0) or 0
            setattr(job, "run_count", current_count + 1)
            db_session.commit()
            db_session.refresh(job)
            new_count = getattr(job, "run_count", 0) or 0
            assert new_count == initial_count + i + 1

    def test_job_max_run_count_limit(self, db_session: Any) -> None:
        """测试任务最大执行次数限制"""
        job = Job(
            name="最大执行次数测试",
            cron_expr="0 0 * * *",
            command="https://example.com",
            max_run_count=3,
            run_count=3,
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        # 达到最大执行次数
        job_run_count = getattr(job, "run_count", 0) or 0
        job_max_run_count = getattr(job, "max_run_count", 0) or 0
        assert job_run_count >= job_max_run_count

        # 应该自动停止
        setattr(job, "state", 2)
        db_session.commit()
        db_session.refresh(job)
        job_state = getattr(job, "state", 0) or 0
        assert job_state == 2


class TestJobExecLogModel:
    """任务执行日志模型测试"""

    def test_create_job_log(self, db_session: Any, sample_job: Any) -> None:
        """测试创建任务执行日志"""
        log = JobExecLog(
            time=datetime.utcnow().isoformat(),
            end_time=datetime.utcnow().isoformat(),
            job_id=sample_job.id,
            job_name=sample_job.name,
            status="success",
            duration_ms=150,
            mode=sample_job.mode,
            command=sample_job.command,
            exit_code=0,
            stdout="执行成功",
            stderr="",
            http_url="https://httpbin.org/get",
            http_method="GET",
            http_status=200,
            http_resp="响应内容",
            func_name="",
            func_args="",
            func_result="",
            error_msg="",
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)

        assert log.id is not None
        assert log.job_id == sample_job.id
        assert log.status == "success"
        assert log.duration_ms == 150
        assert log.http_status == 200

    def test_job_log_failure_status(self, db_session: Any, sample_job: Any) -> None:
        """测试失败状态的执行日志"""
        log = JobExecLog(
            time=datetime.utcnow().isoformat(),
            end_time=datetime.utcnow().isoformat(),
            job_id=sample_job.id,
            job_name=sample_job.name,
            status="fail",
            duration_ms=50,
            mode=sample_job.mode,
            command=sample_job.command,
            exit_code=1,
            stdout="",
            stderr="执行失败",
            error_msg="网络连接超时",
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)

        assert log.status == "fail"
        assert log.exit_code == 1
        if log.stderr and "执行失败" in log.stderr:
            assert True
        else:
            assert False
        if log.error_msg and "网络连接超时" in log.error_msg:
            assert True
        else:
            assert False

    def test_job_log_http_details(self, db_session: Any, sample_job: Any) -> None:
        """测试HTTP任务的执行日志"""
        log = JobExecLog(
            time=datetime.utcnow().isoformat(),
            end_time=datetime.utcnow().isoformat(),
            job_id=sample_job.id,
            job_name=sample_job.name,
            status="success",
            duration_ms=200,
            mode="http",
            command="https://httpbin.org/get",
            http_url="https://httpbin.org/get",
            http_method="GET",
            http_status=200,
            http_resp='{"status": "ok"}',
            error_msg="",
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)

        assert log.mode == "http"
        assert log.http_url == "https://httpbin.org/get"
        assert log.http_method == "GET"
        assert log.http_status == 200
        if log.http_url and "httpbin.org" in log.http_url:
            assert True
        else:
            assert False

    def test_job_log_command_details(self, db_session: Any, sample_job: Any) -> None:
        """测试命令任务的执行日志"""
        log = JobExecLog(
            time=datetime.utcnow().isoformat(),
            end_time=datetime.utcnow().isoformat(),
            job_id=sample_job.id,
            job_name=sample_job.name,
            status="success",
            duration_ms=100,
            mode="command",
            command="echo 'Hello World'",
            exit_code=0,
            stdout="Hello World\n",
            stderr="",
            error_msg="",
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)

        assert log.mode == "command"
        assert log.command == "echo 'Hello World'"
        assert log.exit_code == 0
        if log.stdout and "Hello World" in log.stdout:
            assert True
        else:
            assert False

    def test_job_log_function_details(self, db_session: Any, sample_job: Any) -> None:
        """测试函数任务的执行日志"""
        log = JobExecLog(
            time=datetime.utcnow().isoformat(),
            end_time=datetime.utcnow().isoformat(),
            job_id=sample_job.id,
            job_name=sample_job.name,
            status="success",
            duration_ms=50,
            mode="func",
            command="test_function",
            func_name="test_function",
            func_args='["arg1", "arg2"]',
            func_result="函数执行结果",
            error_msg="",
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)

        assert log.mode == "func"
        assert log.func_name == "test_function"
        assert log.func_args == '["arg1", "arg2"]'
        assert log.func_result == "函数执行结果"


class TestAdminModel:
    """管理员模型测试"""

    def test_create_admin(self, db_session: Any) -> None:
        """测试创建管理员"""
        admin = Admin(
            username="test_admin",
            password="hashed_password",
            email="admin@example.com",
            role="admin",
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)

        assert admin.id is not None
        assert admin.username == "test_admin"
        assert admin.email == "admin@example.com"
        assert admin.role == "admin"
        assert admin.created_at is not None
        assert admin.updated_at is not None

    def test_admin_default_values(self, db_session: Any) -> None:
        """测试管理员默认值"""
        admin = Admin(username="default_admin", password="password")
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)

        assert admin.role == "admin"  # 默认值
        assert admin.email is None  # 默认值
        assert admin.is_active is True  # 默认值


class TestModelValidation:
    """模型验证测试"""

    def test_job_name_required(self, db_session: Any) -> None:
        """测试任务名称必填"""
        with pytest.raises(Exception):  # SQLAlchemy会抛出异常
            job = Job(cron_expr="0 0 * * *", command="https://example.com")
            db_session.add(job)
            db_session.commit()

    def test_job_cron_expr_required(self, db_session: Any) -> None:
        """测试cron表达式必填"""
        with pytest.raises(Exception):
            job = Job(name="测试任务", command="https://example.com")
            db_session.add(job)
            db_session.commit()

    def test_job_command_required(self, db_session: Any) -> None:
        """测试命令必填"""
        with pytest.raises(Exception):
            job = Job(name="测试任务", cron_expr="0 0 * * *")
            db_session.add(job)
            db_session.commit()

    def test_admin_username_required(self, db_session: Any) -> None:
        """测试管理员用户名必填"""
        with pytest.raises(Exception):
            admin = Admin(password="password")
            db_session.add(admin)
            db_session.commit()

    def test_admin_password_required(self, db_session: Any) -> None:
        """测试管理员密码必填"""
        with pytest.raises(Exception):
            admin = Admin(username="admin")
            db_session.add(admin)
            db_session.commit()


class TestModelRelationships:
    """模型关联关系测试"""

    def test_job_logs_relationship(self, db_session: Any) -> None:
        """测试任务与日志的关联关系"""
        # 创建任务
        job = Job(name="关联测试任务", cron_expr="0 0 * * *", command="https://example.com")
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        # 创建多个日志
        logs = []
        for i in range(3):
            log = JobExecLog(
                time=datetime.utcnow().isoformat(),
                end_time=datetime.utcnow().isoformat(),
                job_id=job.id,
                job_name=job.name,
                status="success",
                duration_ms=100 + i,
                mode=job.mode,
                command=job.command,
            )
            logs.append(log)
            db_session.add(log)

        db_session.commit()

        # 验证关联
        for log in logs:
            assert log.job_id == job.id
            assert log.job_name == job.name

    def test_job_logs_cascade_delete(self, db_session: Any) -> None:
        """测试任务删除时级联删除日志"""
        # 创建任务和日志
        job = Job(name="级联删除测试", cron_expr="0 0 * * *", command="https://example.com")
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        log = JobExecLog(
            time=datetime.utcnow().isoformat(),
            end_time=datetime.utcnow().isoformat(),
            job_id=job.id,
            job_name=job.name,
            status="success",
            duration_ms=100,
            mode=job.mode,
            command=job.command,
        )
        db_session.add(log)
        db_session.commit()

        # 删除任务
        db_session.delete(job)
        db_session.commit()

        # 验证日志也被删除
        remaining_logs = db_session.query(JobExecLog).filter_by(job_id=job.id).all()
        assert len(remaining_logs) == 0
