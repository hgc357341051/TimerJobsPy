"""
API接口测试
测试所有API端点的功能
"""

from typing import Any


class TestJobAPI:
    """任务API测试"""

    def test_create_job_success(self, client: Any, valid_job_data: Any) -> None:
        """测试成功创建任务"""
        response = client.post("/jobs/add", json=valid_job_data)
        assert response.status_code == 200
        data = response.json()
        assert "任务创建成功" in data["msg"]
        assert data["code"] == 200

    def test_create_job_invalid_data(self, client: Any, invalid_job_data: Any) -> None:
        """测试创建任务时无效数据"""
        response = client.post("/jobs/add", json=invalid_job_data)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 422

    def test_create_job_missing_required_fields(self, client: Any) -> None:
        """测试创建任务时缺少必填字段"""
        response = client.post("/jobs/add", json={})
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 422

    def test_get_job_list(self, client: Any, sample_job: Any) -> None:
        """测试获取任务列表"""
        response = client.get("/jobs/list")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_get_job_detail(self, client: Any, sample_job: Any) -> None:
        """测试获取任务详情"""
        response = client.get(f"/jobs/read?id={sample_job.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["id"] == sample_job.id
        assert data["data"]["name"] == sample_job.name

    def test_get_job_detail_not_found(self, client: Any) -> None:
        """测试获取不存在的任务详情"""
        response = client.get("/jobs/read?id=99999")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 404

    def test_update_job(self, client: Any, sample_job: Any) -> None:
        """测试更新任务"""
        update_data = {"name": "更新后的任务名称"}
        response = client.post(f"/jobs/edit?id={sample_job.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert "任务更新成功" in data["msg"]
        assert data["code"] == 200

    def test_update_job_not_found(self, client: Any) -> None:
        """测试更新不存在的任务"""
        update_data = {"name": "更新后的任务名称"}
        response = client.post("/jobs/edit?id=99999", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 404

    def test_delete_job(self, client: Any, sample_job: Any) -> None:
        """测试删除任务"""
        response = client.post(f"/jobs/del?id={sample_job.id}")
        assert response.status_code == 200
        data = response.json()
        assert "任务删除成功" in data["msg"]
        assert data["code"] == 200

    def test_delete_job_not_found(self, client: Any) -> None:
        """测试删除不存在的任务"""
        response = client.post("/jobs/del?id=99999")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 404

    def test_run_job(self, client: Any, sample_job: Any) -> None:
        """测试手动运行任务"""
        response = client.post(f"/jobs/run?id={sample_job.id}")
        assert response.status_code == 200
        data = response.json()
        assert "任务已手动触发" in data["msg"]
        assert data["code"] == 200

    def test_stop_job(self, client: Any, sample_job: Any) -> None:
        """测试停止任务"""
        response = client.post(f"/jobs/stop?id={sample_job.id}")
        assert response.status_code == 200
        data = response.json()
        assert "任务已停止" in data["msg"]
        assert data["code"] == 200

    def test_restart_job(self, client: Any, sample_job: Any) -> None:
        """测试重启任务"""
        response = client.post(f"/jobs/restart?id={sample_job.id}")
        assert response.status_code == 200
        data = response.json()
        assert "任务已重启" in data["msg"]
        assert data["code"] == 200

    def test_run_all_jobs(self, client: Any, sample_job: Any) -> None:
        """测试运行所有任务"""
        response = client.post("/jobs/runAll")
        assert response.status_code == 200
        data = response.json()
        assert "所有任务已手动触发" in data["msg"]
        assert data["code"] == 200

    def test_stop_all_jobs(self, client: Any, sample_job: Any) -> None:
        """测试停止所有任务"""
        response = client.post("/jobs/stopAll")
        assert response.status_code == 200
        data = response.json()
        assert "所有任务已停止" in data["msg"]
        assert data["code"] == 200

    def test_job_state(self, client: Any, sample_job: Any) -> None:
        """测试获取任务状态"""
        response = client.get("/jobs/jobState")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data["data"]
        assert "running" in data["data"]
        assert "stopped" in data["data"]

    def test_job_status(self, client: Any, sample_job: Any) -> None:
        """测试获取任务状态详情"""
        response = client.get("/jobs/jobStatus")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "running" in data
        assert "waiting" in data
        assert "stopped" in data

    def test_scheduler_tasks(self, client: Any) -> None:
        """测试获取调度器任务"""
        response = client.get("/jobs/scheduler")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or isinstance(data.get("data", []), list)

    def test_calibrate_jobs(self, client: Any) -> None:
        """测试任务校准"""
        response = client.post("/jobs/checkJob")
        assert response.status_code == 200
        data = response.json()
        assert "任务调度器已校准" in data["msg"]
        assert data["code"] == 200


class TestJobLogsAPI:
    """任务日志API测试"""

    def test_get_job_logs(self, client: Any, sample_job: Any) -> None:
        """测试获取任务日志"""
        response = client.post(f"/jobs/logs?id={sample_job.id}")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_get_job_logs_with_pagination(self, client: Any, sample_job: Any) -> None:
        """测试分页获取任务日志"""
        response = client.post(f"/jobs/logs?id={sample_job.id}&page=1&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "data" in data

    def test_get_job_logs_with_date_filter(self, client: Any, sample_job: Any) -> None:
        """测试按日期过滤任务日志"""
        response = client.post(f"/jobs/logs?id={sample_job.id}&date=2024-01-01")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "data" in data


class TestSystemAPI:
    """系统API测试"""

    def test_health_check(self, client: Any) -> None:
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_get_functions(self, client: Any) -> None:
        """测试获取可用函数"""
        response = client.get("/jobs/functions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_reload_functions(self, client: Any) -> None:
        """测试重新加载函数"""
        response = client.post("/jobs/functions/reload")
        assert response.status_code == 200
        data = response.json()
        assert "已热加载" in data["msg"]
        assert data["code"] == 200

    def test_get_db_info(self, client: Any) -> None:
        """测试获取数据库信息"""
        response = client.get("/jobs/dbinfo")
        assert response.status_code == 200
        data = response.json()
        assert "db_url" in data

    def test_reload_config(self, client: Any) -> None:
        """测试重载配置"""
        response = client.post("/jobs/reload-config")
        assert response.status_code == 200
        data = response.json()
        assert "配置已热重载" in data["msg"]
        assert data["code"] == 200


class TestIPControlAPI:
    """IP控制API测试"""

    def test_get_ip_control_status(self, client: Any) -> None:
        """测试获取IP控制状态"""
        response = client.get("/jobs/ip-control/status")
        assert response.status_code == 200
        data = response.json()
        assert "whitelist" in data
        assert "blacklist" in data

    def test_add_to_whitelist(self, client: Any) -> None:
        """测试添加IP到白名单"""
        response = client.post("/jobs/ip-control/whitelist/add?ip=192.168.1.1")
        assert response.status_code == 200
        data = response.json()
        assert "added to whitelist" in data["msg"]
        assert data["code"] == 200

    def test_remove_from_whitelist(self, client: Any) -> None:
        """测试从白名单移除IP"""
        response = client.post("/jobs/ip-control/whitelist/remove?ip=192.168.1.1")
        assert response.status_code == 200
        data = response.json()
        assert "removed from whitelist" in data["msg"]
        assert data["code"] == 200

    def test_add_to_blacklist(self, client: Any) -> None:
        """测试添加IP到黑名单"""
        response = client.post("/jobs/ip-control/blacklist/add?ip=192.168.1.100")
        assert response.status_code == 200
        data = response.json()
        assert "added to blacklist" in data["msg"]
        assert data["code"] == 200

    def test_remove_from_blacklist(self, client: Any) -> None:
        """测试从黑名单移除IP"""
        response = client.post("/jobs/ip-control/blacklist/remove?ip=192.168.1.100")
        assert response.status_code == 200
        data = response.json()
        assert "removed from blacklist" in data["msg"]
        assert data["code"] == 200


class TestValidationErrors:
    """验证错误测试"""

    def test_invalid_cron_expression(self, client: Any) -> None:
        """测试无效的cron表达式"""
        job_data = {
            "name": "测试任务",
            "cron_expr": "invalid_cron",
            "command": "https://example.com",
            "mode": "http",
        }
        response = client.post("/jobs/add", json=job_data)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 422

    def test_invalid_job_mode(self, client: Any) -> None:
        """测试无效的任务模式"""
        job_data = {
            "name": "测试任务",
            "cron_expr": "0 0 * * *",
            "command": "https://example.com",
            "mode": "invalid_mode",
        }
        response = client.post("/jobs/add", json=job_data)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 422

    def test_empty_job_name(self, client: Any) -> None:
        """测试空任务名称"""
        job_data = {
            "name": "",
            "cron_expr": "0 0 * * *",
            "mode": "http",
            "command": "https://example.com",
        }
        response = client.post("/jobs/add", json=job_data)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 422
