#!/usr/bin/env python3
"""
Python版本检查脚本
检查当前Python版本是否满足项目要求
"""

import sys
import platform
from typing import Tuple


def get_version_info() -> Tuple[int, int, int]:
    """获取Python版本信息"""
    return sys.version_info.major, sys.version_info.minor, sys.version_info.micro


def check_python_version() -> bool:
    """检查Python版本兼容性"""
    major, minor, micro = get_version_info()

    print("🐍 Python版本检查")
    print("=" * 50)
    print(f"当前版本: Python {major}.{minor}.{micro}")
    print(f"平台: {platform.platform()}")
    print(f"架构: {platform.architecture()[0]}")
    print()

    # 检查最低版本要求
    if major < 3 or (major == 3 and minor < 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print("请升级Python版本后重试")
        return False

    # 版本评级
    if major == 3 and minor >= 11:
        print("✅ 优秀版本 (Python 3.11+)")
        print("   - 最佳性能")
        print("   - 最新特性")
        print("   - 推荐用于生产环境")
    elif major == 3 and minor >= 10:
        print("✅ 推荐版本 (Python 3.10+)")
        print("   - 稳定性好")
        print("   - 性能优秀")
        print("   - 推荐用于生产环境")
    elif major == 3 and minor >= 9:
        print("✅ 良好版本 (Python 3.9+)")
        print("   - 功能完善")
        print("   - 兼容性好")
        print("   - 适合开发和生产")
    elif major == 3 and minor >= 8:
        print("⚠️  最低支持版本 (Python 3.8+)")
        print("   - 基本功能支持")
        print("   - 建议升级到更新版本")
        print("   - 仅用于兼容性考虑")

    print()
    print("📋 版本建议:")
    print("   - 生产环境: Python 3.10 或 3.11")
    print("   - 开发环境: Python 3.11 或 3.12")
    print("   - 最低要求: Python 3.8")

    return True


def check_dependencies():
    """检查关键依赖包"""
    print("\n📦 依赖包检查")
    print("=" * 50)

    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "apscheduler",
        "requests",
        "pydantic",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (未安装)")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
    else:
        print("\n✅ 所有依赖包已安装")
        return True


def check_environment():
    """检查运行环境"""
    print("\n🔧 环境检查")
    print("=" * 50)

    # 检查虚拟环境
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )
    if in_venv:
        print("✅ 运行在虚拟环境中")
    else:
        print("⚠️  未使用虚拟环境")
        print("   建议使用虚拟环境以避免依赖冲突")

    # 检查工作目录
    import os

    if os.path.exists("app") and os.path.exists("cli.py"):
        print("✅ 项目目录结构正确")
    else:
        print("❌ 项目目录结构不正确")
        print("   请确保在项目根目录下运行此脚本")
        return False

    return True


def main():
    """主函数"""
    print("小胡定时任务系统（Python版） - 环境检查")
    print("=" * 60)

    # 检查Python版本
    if not check_python_version():
        sys.exit(1)

    # 检查环境
    if not check_environment():
        sys.exit(1)

    # 检查依赖包
    check_dependencies()

    print("\n" + "=" * 60)
    print("🎉 环境检查完成！")
    print("如果所有检查都通过，您可以开始使用系统了。")
    print("\n启动命令:")
    print("  python cli.py start        # 前台模式")
    print("  python cli.py start -d     # 后台模式")
    print("  python cli.py start -d -f  # 守护进程模式")


if __name__ == "__main__":
    main()
