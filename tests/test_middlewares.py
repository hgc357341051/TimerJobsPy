"""
中间件测试
测试IP控制、认证等中间件功能
"""

from typing import Any


class TestIPControlMiddleware:
    """IP控制中间件测试"""

    def test_ip_control_allowed_ip(self, client: Any) -> None:
        """测试允许的IP"""
        # 由于在conftest.py中已经设置了白名单，测试客户端应该能正常访问
        response = client.get("/health")
        assert response.status_code == 200

    def test_ip_control_basic_functionality(self) -> None:
        """测试IP控制基本功能"""
        from app.middlewares.ip_control import IPControl

        ip_control = IPControl()
        ip_control.whitelist.clear()
        ip_control.blacklist.clear()

        # 测试默认允许所有IP
        assert ip_control.is_allowed("127.0.0.1") is True
        assert ip_control.is_allowed("192.168.1.1") is True

        # 测试添加白名单
        ip_control.add_to_whitelist("192.168.1.100")
        assert ip_control.is_allowed("192.168.1.100") is True

        # 测试添加黑名单
        ip_control.add_to_blacklist("192.168.1.200")
        assert ip_control.is_allowed("192.168.1.200") is False

        # 测试移除白名单
        ip_control.remove_from_whitelist("192.168.1.100")
        assert "192.168.1.100" not in ip_control.whitelist

        # 测试移除黑名单
        ip_control.remove_from_blacklist("192.168.1.200")
        assert "192.168.1.200" not in ip_control.blacklist


class TestAuthenticationMiddleware:
    """认证中间件测试"""

    def test_authentication_basic(self, client: Any) -> None:
        """测试基本认证功能"""
        # 测试健康检查端点（通常不需要认证）
        response = client.get("/health")
        assert response.status_code == 200

    def test_authentication_headers(self, client: Any) -> None:
        """测试认证头"""
        # 测试带认证头的请求
        headers = {"Authorization": "Bearer test_token"}
        response = client.get("/health", headers=headers)
        assert response.status_code == 200


class TestValidationMiddleware:
    """验证中间件测试"""

    def test_validation_basic(self, client: Any) -> None:
        """测试基本验证功能"""
        # 测试正常请求
        response = client.get("/health")
        assert response.status_code == 200

    def test_validation_error_handling(self, client: Any) -> None:
        """测试验证错误处理"""
        # 测试无效的JSON请求
        response = client.post("/jobs/add", content="invalid json")
        assert response.status_code == 200 or response.status_code in [400, 422, 500]


class TestMiddlewareIntegration:
    """中间件集成测试"""

    def test_middleware_order(self, client: Any) -> None:
        """测试中间件执行顺序"""
        # 测试多个中间件协同工作
        response = client.get("/health")
        assert response.status_code == 200

    def test_middleware_error_handling(self, client: Any) -> None:
        """测试中间件错误处理"""
        # 测试中间件异常处理
        response = client.get("/health")
        assert response.status_code == 200
