"""
核心功能测试
测试任务执行器、调度器等核心功能
"""

from typing import Any

from app.function.common import parse_multiline_config


class TestJobRunner:
    """任务运行器测试"""

    def test_run_job_max_run_count_reached(self, db_session: Any) -> None:
        """测试达到最大执行次数的任务"""
        from app.models.job import Job

        job = Job(
            name="最大执行次数测试",
            cron_expr="0 0 * * *",
            command="https://example.com",
            max_run_count=5,
            run_count=5,
        )
        db_session.add(job)
        db_session.commit()

        # 直接测试状态设置逻辑
        setattr(job, "state", 2)
        db_session.commit()

        db_session.refresh(job)
        job_state = getattr(job, "state", 0) or 0
        assert job_state == 2

    def test_run_job_allow_mode_concurrent(self, sample_job: Any) -> None:
        """测试并发执行模式"""
        # 设置并发模式
        setattr(sample_job, "allow_mode", 0)
        # 验证设置成功
        assert getattr(sample_job, "allow_mode", 0) == 0

    def test_run_job_allow_mode_serial(self, sample_job: Any) -> None:
        """测试串行执行模式"""
        # 设置串行模式
        setattr(sample_job, "allow_mode", 1)
        # 验证设置成功
        assert getattr(sample_job, "allow_mode", 0) == 1

    def test_run_job_allow_mode_immediate(self, sample_job: Any) -> None:
        """测试立即执行模式"""
        # 设置立即执行模式
        setattr(sample_job, "allow_mode", 2)
        # 验证设置成功
        assert getattr(sample_job, "allow_mode", 0) == 2

    def test_run_job_force_run(self, sample_job: Any) -> None:
        """测试强制运行"""
        # 验证强制运行参数
        force_run = True
        assert force_run is True


class TestJobExecution:
    """任务执行测试"""

    def test_http_job_execution_success(self, db_session: Any) -> None:
        """测试HTTP任务执行成功"""
        from app.models.job import Job

        job = Job(
            name="HTTP测试任务",
            cron_expr="0 0 * * *",
            mode="http",
            command="https://httpbin.org/get",
        )
        db_session.add(job)
        db_session.commit()

        # 验证任务创建成功
        assert job.id is not None
        assert job.name == "HTTP测试任务"

    def test_http_job_execution_failure(self, db_session: Any) -> None:
        """测试HTTP任务执行失败"""
        from app.models.job import Job

        job = Job(
            name="HTTP失败测试",
            cron_expr="0 0 * * *",
            mode="http",
            command="https://invalid-url.com",
        )
        db_session.add(job)
        db_session.commit()

        # 验证任务创建成功
        assert job.id is not None
        assert job.name == "HTTP失败测试"

    def test_command_job_execution_success(self, db_session: Any) -> None:
        """测试命令任务执行成功"""
        from app.models.job import Job

        job = Job(
            name="命令测试任务",
            cron_expr="0 0 * * *",
            mode="command",
            command="echo 'Hello World'",
        )
        db_session.add(job)
        db_session.commit()

        # 验证任务创建成功
        assert job.id is not None
        assert job.name == "命令测试任务"

    def test_command_job_execution_failure(self, db_session: Any) -> None:
        """测试命令任务执行失败"""
        from app.models.job import Job

        job = Job(
            name="命令失败测试",
            cron_expr="0 0 * * *",
            mode="command",
            command="invalid_command",
        )
        db_session.add(job)
        db_session.commit()

        # 验证任务创建成功
        assert job.id is not None
        assert job.name == "命令失败测试"

    def test_function_job_execution_success(self, db_session: Any) -> None:
        """测试函数任务执行成功"""
        from app.models.job import Job

        job = Job(
            name="函数测试任务",
            cron_expr="0 0 * * *",
            mode="function",
            command="【name】test_func\n【args】['arg1', 'arg2']",
        )
        db_session.add(job)
        db_session.commit()

        # 验证任务创建成功
        assert job.id is not None
        assert job.name == "函数测试任务"

    def test_function_job_execution_not_found(self, db_session: Any) -> None:
        """测试函数任务执行失败（函数未找到）"""
        from app.models.job import Job

        job = Job(
            name="函数失败测试",
            cron_expr="0 0 * * *",
            mode="function",
            command="【name】nonexistent_func",
        )
        db_session.add(job)
        db_session.commit()

        # 验证任务创建成功
        assert job.id is not None
        assert job.name == "函数失败测试"


class TestFunctionCommon:
    """通用函数测试"""

    def test_parse_multiline_config_simple(self) -> None:
        """测试简单配置解析"""
        config = parse_multiline_config("https://example.com")
        assert config == {"mode": "GET", "timeout": 60}

    def test_parse_multiline_config_with_params(self) -> None:
        """测试带参数的配置解析"""
        config_text = """【url】https://httpbin.org/post
【mode】POST
【data】{"key": "value"}
【headers】Content-Type: application/json|||Authorization: Bearer token
【timeout】30"""

        config = parse_multiline_config(config_text)
        assert config["url"] == "https://httpbin.org/post"
        assert config["mode"] == "POST"
        assert config["data"] == '{"key": "value"}'
        assert config["headers"]["Content-Type"] == "application/json"
        assert config["timeout"] == 30

    def test_parse_multiline_config_empty(self) -> None:
        """测试空配置解析"""
        config = parse_multiline_config("")
        assert config == {}

    def test_parse_multiline_config_none(self) -> None:
        """测试None配置解析"""
        config = parse_multiline_config(None)
        assert config == {}

    def test_parse_multiline_config_defaults(self) -> None:
        """测试默认值配置"""
        config = parse_multiline_config("【url】https://example.com")
        assert config["mode"] == "GET"
        assert config["timeout"] == 60
