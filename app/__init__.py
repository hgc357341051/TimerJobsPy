from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api.jobs import router as jobs_router
from app.config import Config
from app.core.job_logger import close_all_job_loggers
from app.core.scheduler import scheduler
from app.middlewares.ip_control import IPControlMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    # 启动时
    print(f"启动 {Config.APP_NAME} v{Config.APP_VERSION}")
    print(f"数据库类型: {Config.DATABASE_TYPE}")
    print(f"服务器端口: {Config.SERVER_PORT}")
    print(f"IP控制: {'启用' if Config.IP_CONTROL_ENABLED else '禁用'}")

    # 启动调度器
    scheduler.start()
    print("调度器已启动")

    yield

    # 关闭时
    print("正在关闭调度器...")
    scheduler.shutdown()

    # 关闭所有日志文件句柄
    print("正在关闭日志文件句柄...")
    close_all_job_loggers()

    print("应用已关闭")


# 创建FastAPI应用
app = FastAPI(
    title=Config.API_TITLE,
    description=Config.API_DESCRIPTION,
    version=Config.API_VERSION,
    docs_url=Config.API_DOCS_URL,
    redoc_url=Config.API_REDOC_URL,
    lifespan=lifespan,
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# 添加IP控制中间件
if Config.IP_CONTROL_ENABLED:
    app.add_middleware(IPControlMiddleware)

# 注册路由
app.include_router(jobs_router, prefix="/api/v1", tags=["任务管理"])


@app.get("/")
async def root() -> Dict[str, Any]:
    """根路径"""
    return {
        "code": 200,
        "msg": "小胡定时任务系统运行正常",
        "data": {
            "app_name": Config.APP_NAME,
            "version": Config.APP_VERSION,
            "database_type": Config.DATABASE_TYPE,
            "server_port": Config.SERVER_PORT,
        },
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """健康检查"""
    return {
        "code": 200,
        "msg": "系统健康",
        "data": {
            "status": "healthy",
            "scheduler_running": scheduler.running,
            "job_count": len(scheduler.get_jobs()),
        },
    }
