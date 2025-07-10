import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import jobs
from app.config import Config
from app.core.job_logger import close_all_job_loggers
from app.core.scheduler import start_scheduler
from app.deps import engine
from app.function.registry import hot_reload
from app.middlewares.ip_control import IPControlMiddleware
from app.middlewares.validation import register_validation_handlers
from app.models.base import Base, error_response


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # 确保运行时目录和备份目录存在
    for directory in [Config.RUNTIME_DIR, Config.BACKUP_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"已创建目录: {directory}")
    
    # 启动时执行
    Base.metadata.create_all(bind=engine)

    # 加载用户函数
    user_funcs_dir = os.path.join(os.path.dirname(__file__), "function", "user_funcs")
    hot_reload(user_funcs_dir)
    print(f"已加载用户函数目录: {user_funcs_dir}")

    # 启动调度器
    start_scheduler()

    yield
    # 关闭时执行
    # 关闭所有任务日志文件句柄
    close_all_job_loggers()
    print("已关闭所有任务日志文件句柄")


app = FastAPI(
    title="小胡定时任务系统",
    description="企业级定时任务调度系统",
    version="1.0.0",
    lifespan=lifespan,
)

# 注册中文化异常处理器
register_validation_handlers(app)

# 集成IP控制中间件
app.add_middleware(IPControlMiddleware)

# 路由注册
app.include_router(jobs.router)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content=error_response(msg=f"HTTP错误: {exc.detail}", code=exc.status_code),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content=error_response(msg=f"参数验证错误: {exc.errors()}", code=404),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content=error_response(msg=f"服务器内部错误: {str(exc)}", code=500),
    )
