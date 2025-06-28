"""
Locust性能测试文件
用于测试API的性能和并发能力
"""

from typing import Any

from locust import HttpUser, between, events, task


class JobAPIUser(HttpUser):
    """任务API用户"""

    wait_time = between(1, 3)  # 请求间隔1-3秒

    def on_start(self) -> None:
        """用户开始时的初始化"""
        pass

    @task(3)
    def get_job_list(self) -> None:
        """获取任务列表"""
        self.client.get("/jobs/list")

    @task(2)
    def get_job_status(self) -> None:
        """获取任务状态"""
        self.client.get("/jobs/jobState")

    @task(1)
    def create_job(self) -> None:
        """创建任务"""
        env = getattr(self.client, "environment", None)
        user_count = 0
        if env and hasattr(env, "runner") and hasattr(env.runner, "user_count"):
            user_count = env.runner.user_count
        job_data = {
            "name": f"性能测试任务_{user_count}",
            "desc": "性能测试创建的任务",
            "cron_expr": "0 0 * * *",
            "mode": "http",
            "command": "https://httpbin.org/get",
            "allow_mode": 0,
            "max_run_count": 5,
        }
        self.client.post("/jobs/add", json=job_data)

    @task(2)
    def run_job(self) -> None:
        """运行任务（假设任务ID为1）"""
        self.client.post("/jobs/run?id=1")

    @task(1)
    def stop_job(self) -> None:
        """停止任务（假设任务ID为1）"""
        self.client.post("/jobs/stop?id=1")

    @task(1)
    def get_functions(self) -> None:
        """获取可用函数"""
        self.client.get("/jobs/functions")

    @task(1)
    def health_check(self) -> None:
        """健康检查"""
        self.client.get("/health")


class AdminAPIUser(HttpUser):
    """管理员API用户"""

    wait_time = between(2, 5)  # 管理员操作间隔更长

    def on_start(self) -> None:
        """用户开始时的初始化"""
        pass

    @task(2)
    def get_job_logs(self) -> None:
        """获取任务日志"""
        self.client.post("/jobs/logs?id=1")

    @task(1)
    def get_scheduler_info(self) -> None:
        """获取调度器信息"""
        self.client.get("/jobs/scheduler")

    @task(1)
    def calibrate_jobs(self) -> None:
        """校准任务"""
        self.client.post("/jobs/checkJob")

    @task(1)
    def reload_functions(self) -> None:
        """重新加载函数"""
        self.client.post("/jobs/functions/reload")

    @task(1)
    def get_db_info(self) -> None:
        """获取数据库信息"""
        self.client.get("/jobs/dbinfo")


class IPControlUser(HttpUser):
    """IP控制API用户"""

    wait_time = between(5, 10)  # IP控制操作间隔最长

    def on_start(self) -> None:
        """用户开始时的初始化"""
        pass

    @task(1)
    def get_ip_control_status(self) -> None:
        """获取IP控制状态"""
        self.client.get("/jobs/ip-control/status")

    @task(1)
    def add_to_whitelist(self) -> None:
        """添加到白名单"""
        self.client.post("/jobs/ip-control/whitelist/add?ip=192.168.1.100")

    @task(1)
    def remove_from_whitelist(self) -> None:
        """从白名单移除"""
        self.client.post("/jobs/ip-control/whitelist/remove?ip=192.168.1.100")

    @task(1)
    def add_to_blacklist(self) -> None:
        """添加到黑名单"""
        self.client.post("/jobs/ip-control/blacklist/add?ip=10.0.0.100")

    @task(1)
    def remove_from_blacklist(self) -> None:
        """从黑名单移除"""
        self.client.post("/jobs/ip-control/blacklist/remove?ip=10.0.0.100")


class HeavyLoadUser(HttpUser):
    """高负载用户"""

    wait_time = between(0.1, 0.5)  # 快速请求

    def on_start(self) -> None:
        """用户开始时的初始化"""
        pass

    @task(5)
    def rapid_job_operations(self) -> None:
        """快速任务操作"""
        env = getattr(self.client, "environment", None)
        user_count = 0
        if env and hasattr(env, "runner") and hasattr(env.runner, "user_count"):
            user_count = env.runner.user_count
        job_data = {
            "name": f"高负载任务_{user_count}_{user_count}",
            "desc": "高负载测试任务",
            "cron_expr": "*/1 * * * *",
            "mode": "http",
            "command": "https://httpbin.org/status/200",
            "allow_mode": 0,
            "max_run_count": 1,
        }
        self.client.post("/jobs/add", json=job_data)
        self.client.post("/jobs/run?id=1")
        self.client.get("/jobs/jobState")

    @task(3)
    def concurrent_requests(self) -> None:
        """并发请求"""
        # 同时发送多个请求
        self.client.get("/jobs/list")
        self.client.get("/health")
        self.client.get("/jobs/functions")

    @task(2)
    def batch_operations(self) -> None:
        """批量操作"""
        env = getattr(self.client, "environment", None)
        user_count = 0
        if env and hasattr(env, "runner") and hasattr(env.runner, "user_count"):
            user_count = env.runner.user_count
        for i in range(3):
            job_data = {
                "name": f"批量任务_{i}_{user_count}",
                "desc": f"批量测试任务 {i}",
                "cron_expr": "0 0 * * *",
                "mode": "http",
                "command": "https://httpbin.org/get",
                "allow_mode": 0,
                "max_run_count": 1,
            }
            self.client.post("/jobs/add", json=job_data)


class ReadOnlyUser(HttpUser):
    """只读用户"""

    wait_time = between(1, 2)

    def on_start(self) -> None:
        """用户开始时的初始化"""
        pass

    @task(4)
    def read_operations(self) -> None:
        """只读操作"""
        self.client.get("/jobs/list")
        self.client.get("/jobs/jobState")
        self.client.get("/jobs/jobStatus")
        self.client.get("/jobs/scheduler")
        self.client.get("/health")

    @task(1)
    def get_job_detail(self) -> None:
        """获取任务详情"""
        self.client.get("/jobs/read?id=1")

    @task(1)
    def get_job_logs(self) -> None:
        """获取任务日志"""
        self.client.post("/jobs/logs?id=1")


# 自定义事件监听器
@events.test_start.add_listener  # type: ignore
def on_test_start(environment: Any, **kwargs: Any) -> None:
    """测试开始时的回调"""
    print("🚀 性能测试开始")
    print(f"目标主机: {environment.host}")
    user_count = getattr(getattr(environment, "runner", None), "user_count", 0)
    print(f"用户数量: {user_count}")


@events.test_stop.add_listener  # type: ignore
def on_test_stop(environment: Any, **kwargs: Any) -> None:
    """测试结束时的回调"""
    print("🏁 性能测试结束")

    # 输出统计信息
    stats = environment.stats
    print(f"总请求数: {stats.total.num_requests}")
    print(f"失败请求数: {stats.total.num_failures}")
    print(f"平均响应时间: {stats.total.avg_response_time:.2f}ms")
    print(f"最大响应时间: {stats.total.max_response_time:.2f}ms")
    print(f"最小响应时间: {stats.total.min_response_time:.2f}ms")
    print(f"RPS: {stats.total.current_rps:.2f}")


@events.request.add_listener  # type: ignore
def on_request(
    request_type: str,
    name: str,
    response_time: float,
    response_length: int,
    response: Any,
    context: Any,
    exception: Any,
    start_time: float,
    url: str,
    **kwargs: Any,
) -> None:
    """请求事件监听器"""
    if exception:
        print(f"❌ 请求失败: {name} - {exception}")
    elif response.status_code >= 400:
        print(f"⚠️ 请求错误: {name} - {response.status_code}")
    else:
        print(f"✅ 请求成功: {name} - {response_time:.2f}ms")
