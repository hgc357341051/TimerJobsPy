@echo off
REM 小胡定时任务系统（Python版）启动脚本（Windows）

setlocal enabledelayedexpansion

REM 设置颜色代码
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM 获取脚本目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM 显示帮助信息
if "%1"=="help" goto :show_help
if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help
if "%1"=="" goto :show_help

REM 检查Python环境
call :check_python
if errorlevel 1 exit /b 1

REM 检查依赖
call :check_dependencies
if errorlevel 1 exit /b 1

REM 解析命令
if "%1"=="start" goto :start_service
if "%1"=="start-bg" goto :start_background
if "%1"=="start-daemon" goto :start_daemon
if "%1"=="stop" goto :stop_service
if "%1"=="stop-all" goto :stop_all
if "%1"=="restart" goto :restart_service
if "%1"=="status" goto :show_status
if "%1"=="reload" goto :reload_config

echo %RED%未知命令: %1%NC%
echo.
goto :show_help

:show_help
echo %BLUE%小胡定时任务系统（Python版）启动脚本%NC%
echo.
echo 用法: %0 [命令] [选项]
echo.
echo 命令:
echo   start          启动服务（前台模式）
echo   start-bg       启动服务（后台模式）
echo   start-daemon   启动服务（守护进程模式）
echo   stop           停止服务
echo   stop-all       停止所有相关进程
echo   restart        重启服务
echo   status         查看服务状态
echo   reload         重载配置
echo   help           显示此帮助信息
echo.
echo 选项:
echo   -p PORT        指定端口（默认: 8000）
echo   -H HOST        指定主机（默认: 0.0.0.0）
echo   --reload       开发模式热重载
echo.
echo 示例:
echo   %0 start                    # 前台模式启动
echo   %0 start-bg                 # 后台模式启动
echo   %0 start-daemon             # 守护进程模式启动
echo   %0 stop                     # 停止服务
echo   %0 status                   # 查看状态
echo   %0 start -p 8080            # 指定端口启动
echo   %0 start --reload           # 开发模式启动
goto :eof

:check_python
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%错误: 未找到 python%NC%
    echo 请安装 Python 3.8 或更高版本
    exit /b 1
)

REM 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo %YELLOW%检测到虚拟环境，正在激活...%NC%
    call venv\Scripts\activate.bat
)
goto :eof

:check_dependencies
if not exist "requirements.txt" (
    echo %RED%错误: 未找到 requirements.txt%NC%
    exit /b 1
)

if not exist "cli.py" (
    echo %RED%错误: 未找到 cli.py%NC%
    exit /b 1
)
goto :eof

:start_service
echo %GREEN%启动小胡定时任务系统...%NC%
echo %BLUE%模式: 前台模式%NC%
set "cmd=python cli.py start"
call :add_options
echo %BLUE%执行命令: !cmd!%NC%
!cmd!
goto :eof

:start_background
echo %GREEN%启动小胡定时任务系统...%NC%
echo %BLUE%模式: 后台模式%NC%
set "cmd=python cli.py start -d"
call :add_options
echo %BLUE%执行命令: !cmd!%NC%
!cmd!
goto :eof

:start_daemon
echo %GREEN%启动小胡定时任务系统...%NC%
echo %BLUE%模式: 守护进程模式%NC%
set "cmd=python cli.py start -d -f"
call :add_options
echo %BLUE%执行命令: !cmd!%NC%
!cmd!
goto :eof

:add_options
shift
:add_options_loop
if "%1"=="" goto :eof
if "%1"=="-p" (
    set "cmd=!cmd! -p %2"
    shift
    shift
    goto :add_options_loop
)
if "%1"=="-H" (
    set "cmd=!cmd! -H %2"
    shift
    shift
    goto :add_options_loop
)
if "%1"=="--reload" (
    set "cmd=!cmd! --reload"
    shift
    goto :add_options_loop
)
echo %RED%未知选项: %1%NC%
exit /b 1

:stop_service
echo %YELLOW%停止服务...%NC%
python cli.py stop
goto :eof

:stop_all
echo %YELLOW%停止所有相关进程...%NC%
python cli.py stop -f
goto :eof

:show_status
echo %BLUE%查看服务状态...%NC%
python cli.py status
goto :eof

:restart_service
echo %YELLOW%重启服务...%NC%
python cli.py restart
goto :eof

:reload_config
echo %YELLOW%重载配置...%NC%
python cli.py reload
goto :eof 