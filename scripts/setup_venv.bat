@echo off
chcp 65001 >nul
echo 🚀 自动生成Python虚拟环境脚本
echo ==========================================

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

:: 获取项目根目录
set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

:: 设置虚拟环境名称
set "VENV_NAME=venv"

:: 检查虚拟环境是否已存在
if exist "%VENV_NAME%" (
    echo ⚠️  虚拟环境 '%VENV_NAME%' 已存在
    set /p "REPLY=是否删除现有环境并重新创建? (y/N): "
    if /i "%REPLY%"=="y" (
        echo 🗑️  删除现有虚拟环境...
        :: 先尝试正常删除
        rmdir /s /q "%VENV_NAME%" 2>nul
        if exist "%VENV_NAME%" (
            echo ⚠️  正常删除失败，尝试强制删除...
            :: 使用robocopy强制删除（创建空目录然后删除原目录）
            mkdir "%TEMP%\empty_dir" 2>nul
            robocopy "%TEMP%\empty_dir" "%VENV_NAME%" /MIR /NFL /NDL /NJH /NJS /NC /NS /NP >nul 2>&1
            rmdir /s /q "%VENV_NAME%" 2>nul
            rmdir /s /q "%TEMP%\empty_dir" 2>nul
        )
        if exist "%VENV_NAME%" (
            echo ❌ 无法删除虚拟环境，请手动删除 %VENV_NAME% 目录后重试
            echo 或者关闭所有可能使用该虚拟环境的程序（如IDE、终端等）
            pause
            exit /b 1
        )
        echo ✅ 虚拟环境删除成功
    ) else (
        echo 使用现有虚拟环境
        goto activate_venv
    )
)

:: 创建虚拟环境
echo 🔧 创建虚拟环境: %VENV_NAME%
python -m venv "%VENV_NAME%"
if errorlevel 1 (
    echo ❌ 创建虚拟环境失败
    pause
    exit /b 1
)
echo ✅ 虚拟环境创建成功

:: 升级pip
echo 📦 升级pip...
call "%VENV_NAME%\Scripts\activate.bat"
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ❌ pip升级失败
    pause
    exit /b 1
)
echo ✅ pip升级成功

:: 安装主依赖
echo 📦 安装主依赖包...
call "%VENV_NAME%\Scripts\activate.bat"
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 主依赖安装失败
    pause
    exit /b 1
)
echo ✅ 主依赖安装成功

:: 询问是否安装测试依赖
set /p "INSTALL_TEST=是否安装测试依赖? (y/N): "
if /i "%INSTALL_TEST%"=="y" (
    echo 📦 安装测试依赖包...
    call "%VENV_NAME%\Scripts\activate.bat"
    pip install -r requirements-test.txt
    if errorlevel 1 (
        echo ⚠️  测试依赖安装失败，但主依赖已安装
    ) else (
        echo ✅ 测试依赖安装成功
    )
)

:activate_venv
echo.
echo ==========================================
echo 🎉 虚拟环境设置完成!
echo ==========================================
echo.
echo 📋 激活虚拟环境:
echo    %VENV_NAME%\Scripts\activate.bat
echo.
echo 📁 虚拟环境位置: %PROJECT_ROOT%\%VENV_NAME%
echo 🐍 Python解释器: %PROJECT_ROOT%\%VENV_NAME%\Scripts\python.exe
echo.
echo 💡 提示:
echo    - 激活后可以使用 'deactivate' 退出虚拟环境
echo    - 使用 'pip list' 查看已安装的包
echo    - 使用 'python -m pytest' 运行测试
echo ==========================================
echo.
echo 🔗 现在可以运行以下命令激活虚拟环境:
echo    %VENV_NAME%\Scripts\activate.bat
echo.
pause 