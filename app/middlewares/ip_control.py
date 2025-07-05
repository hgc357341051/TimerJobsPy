import threading
from typing import Any, Callable, Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import Config


class IPControl:
    """IP控制类"""

    def __init__(self) -> None:
        self.whitelist: set[str] = set()
        self.blacklist: set[str] = set()
        self.lock = threading.Lock()
        self._load_config()

    def _load_config(self) -> None:
        """加载配置"""
        # 从配置加载白名单
        if Config.IP_WHITELIST:
            self.whitelist.update(Config.IP_WHITELIST)

        # 从配置加载黑名单
        if Config.IP_BLACKLIST:
            self.blacklist.update(Config.IP_BLACKLIST)

    def is_allowed(self, ip: str) -> bool:
        """检查IP是否允许访问"""
        # 测试环境自动放行 testclient
        if ip == "testclient":
            return True

        # 如果在黑名单中，拒绝访问
        if ip in self.blacklist:
            return False

        # 如果有白名单且IP不在白名单中，拒绝访问
        if self.whitelist and ip not in self.whitelist:
            return False

        return True

    def add_to_whitelist(self, ip: str) -> None:
        """添加到白名单"""
        with self.lock:
            self.whitelist.add(ip)
            self.blacklist.discard(ip)

    def remove_from_whitelist(self, ip: str) -> None:
        """从白名单移除"""
        with self.lock:
            self.whitelist.discard(ip)

    def add_to_blacklist(self, ip: str) -> None:
        """添加到黑名单"""
        with self.lock:
            self.blacklist.add(ip)
            self.whitelist.discard(ip)

    def remove_from_blacklist(self, ip: str) -> None:
        """从黑名单移除"""
        with self.lock:
            self.blacklist.discard(ip)


ip_control = IPControl()


class IPControlMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        client_ip: Optional[str] = request.client.host if request.client else None
        if not client_ip:
            from fastapi.responses import JSONResponse

            from app.models.base import error_response

            return JSONResponse(
                status_code=200, content=error_response(code=400, msg="无法确定客户端IP")
            )
        if not ip_control.is_allowed(client_ip):
            from fastapi.responses import JSONResponse

            from app.models.base import error_response

            return JSONResponse(
                status_code=200,
                content=error_response(code=403, msg=f"IP {client_ip} 不被允许访问"),
            )
        response = await call_next(request)
        return response
