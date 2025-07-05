import os
from typing import Final, List


class Config:
    # 应用基础配置
    APP_NAME: Final[str] = os.getenv("APP_NAME", "小胡测试系统")
    APP_VERSION: Final[str] = os.getenv("APP_VERSION", "1.0.0")

    # 数据库配置
    DATABASE_TYPE: Final[str] = os.getenv("DATABASE_TYPE", "sqlite")  # sqlite 或 mysql

    # MySQL配置（生产环境建议用环境变量覆盖）
    DATABASE_MYSQL_HOST: Final[str] = os.getenv("DATABASE_MYSQL_HOST", "127.0.0.1")
    DATABASE_MYSQL_PORT: Final[int] = int(os.getenv("DATABASE_MYSQL_PORT", "3306"))
    DATABASE_MYSQL_USERNAME: Final[str] = os.getenv("DATABASE_MYSQL_USERNAME", "root")
    DATABASE_MYSQL_PASSWORD: Final[str] = os.getenv(
        "DATABASE_MYSQL_PASSWORD", "root123456"
    )
    DATABASE_MYSQL_DBNAME: Final[str] = os.getenv(
        "DATABASE_MYSQL_DBNAME", "xiaohu_jobs"
    )
    DATABASE_MYSQL_CHARSET: Final[str] = os.getenv("DATABASE_MYSQL_CHARSET", "utf8mb4")
    DATABASE_MYSQL_TABLEPREFIX: Final[str] = os.getenv(
        "DATABASE_MYSQL_TABLEPREFIX", "xiaohus_"
    )
    DATABASE_MYSQL_MAXOPENCONNS: Final[int] = int(
        os.getenv("DATABASE_MYSQL_MAXOPENCONNS", "100")
    )
    DATABASE_MYSQL_MAXIDLECONNS: Final[int] = int(
        os.getenv("DATABASE_MYSQL_MAXIDLECONNS", "20")
    )

    # SQLite配置
    DATABASE_SQLITE_PATH: Final[str] = os.getenv("DATABASE_SQLITE_PATH", "data/jobs.db")
    DATABASE_SQLITE_TABLEPREFIX: Final[str] = os.getenv(
        "DATABASE_SQLITE_TABLEPREFIX", "xiaohus_"
    )
    DATABASE_SQLITE_MAXOPENCONNS: Final[int] = int(
        os.getenv("DATABASE_SQLITE_MAXOPENCONNS", "1")
    )
    DATABASE_SQLITE_MAXIDLECONNS: Final[int] = int(
        os.getenv("DATABASE_SQLITE_MAXIDLECONNS", "1")
    )

    # 日志配置
    LOG_DAYS: Final[int] = int(os.getenv("LOG_DAYS", "3"))
    LOG_ENABLED: Final[bool] = os.getenv("LOG_ENABLED", "true").lower() == "true"
    LOG_LEVELS: Final[List[str]] = os.getenv("LOG_LEVELS", "info,error,warn").split(",")
    LOG_METHODS: Final[List[str]] = (
        os.getenv("LOG_METHODS", "").split(",") if os.getenv("LOG_METHODS") else []
    )

    # 服务器配置
    SERVER_PORT: Final[int] = int(os.getenv("SERVER_PORT", "36363"))
    SERVER_HOST: Final[str] = os.getenv("SERVER_HOST", "0.0.0.0")

    # IP访问控制配置
    IP_CONTROL_ENABLED: Final[bool] = (
        os.getenv("IP_CONTROL_ENABLED", "true").lower() == "true"
    )
    IP_WHITELIST: Final[List[str]] = (
        os.getenv("IP_WHITELIST", "127.0.0.1,::1").split(",")
        if os.getenv("IP_WHITELIST")
        else ["127.0.0.1", "::1"]
    )
    IP_BLACKLIST: Final[List[str]] = (
        os.getenv("IP_BLACKLIST", "").split(",") if os.getenv("IP_BLACKLIST") else []
    )

    # 服务配置
    SERVICE_NAME: Final[str] = os.getenv("SERVICE_NAME", "XiaohuJobService")
    SERVICE_DISPLAY_NAME: Final[str] = os.getenv(
        "SERVICE_DISPLAY_NAME", "小胡专用定时任务系统QQ357341051"
    )
    SERVICE_DESCRIPTION: Final[str] = os.getenv("SERVICE_DESCRIPTION", "小胡专用跨平台任务调度服务")

    # 守护进程配置
    DAEMON_MAX_RESTARTS: Final[int] = int(os.getenv("DAEMON_MAX_RESTARTS", "10"))
    DAEMON_RESTART_DELAY: Final[int] = int(os.getenv("DAEMON_RESTART_DELAY", "5"))

    # 任务日志保留数量
    JOB_LOG_KEEP_COUNT: Final[int] = int(os.getenv("JOB_LOG_KEEP_COUNT", "3"))

    # 安全配置
    SECRET_KEY: Final[str] = os.getenv("SECRET_KEY", "change-me")

    # 函数配置
    FUNC_DIR: Final[str] = os.getenv("FUNC_DIR", "./app/function/user_funcs")

    # 运行时配置
    RUNTIME_DIR: Final[str] = os.getenv("RUNTIME_DIR", "./runtime")
    DATA_DIR: Final[str] = os.getenv("DATA_DIR", "./data")
    BACKUP_DIR: Final[str] = os.getenv("BACKUP_DIR", "./data/backups")

    # 调度器配置
    SCHEDULER_MAX_WORKERS: Final[int] = int(os.getenv("SCHEDULER_MAX_WORKERS", "10"))
    SCHEDULER_JOB_DEFAULTS: Final[dict] = {
        "coalesce": True,
        "max_instances": 1,
        "misfire_grace_time": 60,
    }

    # API配置
    API_TITLE: Final[str] = os.getenv("API_TITLE", "小胡定时任务系统API")
    API_DESCRIPTION: Final[str] = os.getenv("API_DESCRIPTION", "小胡专用跨平台任务调度系统API文档")
    API_VERSION: Final[str] = os.getenv("API_VERSION", "1.0.0")
    API_DOCS_URL: Final[str] = os.getenv("API_DOCS_URL", "/docs")
    API_REDOC_URL: Final[str] = os.getenv("API_REDOC_URL", "/redoc")

    @classmethod
    def get_database_url(cls) -> str:
        """根据配置生成数据库URL"""
        if cls.DATABASE_TYPE.lower() == "mysql":
            return (
                f"mysql+pymysql://{cls.DATABASE_MYSQL_USERNAME}:"
                f"{cls.DATABASE_MYSQL_PASSWORD}@{cls.DATABASE_MYSQL_HOST}:"
                f"{cls.DATABASE_MYSQL_PORT}/{cls.DATABASE_MYSQL_DBNAME}"
                f"?charset={cls.DATABASE_MYSQL_CHARSET}"
            )
        else:
            return f"sqlite:///{cls.DATABASE_SQLITE_PATH}"

    @classmethod
    def get_database_engine_options(cls) -> dict:
        """获取数据库引擎配置选项"""
        if cls.DATABASE_TYPE.lower() == "mysql":
            return {
                "pool_size": cls.DATABASE_MYSQL_MAXOPENCONNS,
                "max_overflow": 0,
                "pool_pre_ping": True,
                "pool_recycle": 3600,
            }
        else:
            return {
                "pool_size": cls.DATABASE_SQLITE_MAXOPENCONNS,
                "max_overflow": 0,
                "pool_pre_ping": True,
            }
