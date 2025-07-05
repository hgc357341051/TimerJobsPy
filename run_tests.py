#!/usr/bin/env python3
"""
测试运行脚本
提供多种测试运行方式
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path


def get_python_executable():
    """获取Python可执行文件路径，优先使用虚拟环境"""
    # 检查是否在虚拟环境中
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # 在虚拟环境中
        return sys.executable
    
    # 检查项目根目录下是否有虚拟环境
    project_root = Path(__file__).parent
    venv_python = project_root / "venv" / "Scripts" / "python.exe"
    
    if venv_python.exists():
        return str(venv_python)
    
    # 检查Unix风格的虚拟环境
    venv_python_unix = project_root / "venv" / "bin" / "python"
    if venv_python_unix.exists():
        return str(venv_python_unix)
    
    # 回退到系统Python
    return sys.executable


# 获取Python可执行文件路径
PYTHON_EXECUTABLE = get_python_executable()


def run_command(cmd, description=""):
    """运行命令并显示结果"""
    print(f"\n{'='*50}")
    print(f"运行: {description}")
    print(f"命令: {' '.join(cmd)}")
    print("=" * 50)

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 成功!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ 失败!")
        print(f"错误代码: {e.returncode}")
        if e.stdout:
            print("标准输出:")
            print(e.stdout)
        if e.stderr:
            print("错误输出:")
            print(e.stderr)
        return False


def install_test_deps():
    """安装测试依赖"""
    print("📦 安装测试依赖...")
    return run_command(
        [PYTHON_EXECUTABLE, "-m", "pip", "install", "-r", "requirements-test.txt"],
        "安装测试依赖",
    )


def run_unit_tests():
    """运行单元测试"""
    print("🧪 运行单元测试...")
    return run_command(
        [PYTHON_EXECUTABLE, "-m", "pytest", "tests/", "-m", "unit", "-v"], "单元测试"
    )


def run_api_tests():
    """运行API测试"""
    print("🌐 运行API测试...")
    return run_command(
        [PYTHON_EXECUTABLE, "-m", "pytest", "tests/test_api.py", "-v"], "API测试"
    )


def run_model_tests():
    """运行模型测试"""
    print("📊 运行模型测试...")
    return run_command(
        [PYTHON_EXECUTABLE, "-m", "pytest", "tests/test_models.py", "-v"], "模型测试"
    )


def run_core_tests():
    """运行核心功能测试..."""
    print("⚙️ 运行核心功能测试...")
    return run_command(
        [PYTHON_EXECUTABLE, "-m", "pytest", "tests/test_core.py", "-v"], "核心功能测试"
    )


def run_all_tests():
    """运行所有测试"""
    print("🚀 运行所有测试...")
    return run_command([sys.executable, "-m", "pytest", "tests/", "-v"], "所有测试")


def run_tests_with_coverage():
    """运行测试并生成覆盖率报告"""
    print("📈 运行测试并生成覆盖率报告...")
    return run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html",
        ],
        "测试覆盖率",
    )


def run_tests_with_html_report():
    """运行测试并生成HTML报告"""
    print("📄 运行测试并生成HTML报告...")
    return run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "--html=test_report.html",
            "--self-contained-html",
        ],
        "HTML测试报告",
    )


def run_specific_test(test_path):
    """运行特定测试"""
    print(f"🎯 运行特定测试: {test_path}")
    return run_command(
        [sys.executable, "-m", "pytest", test_path, "-v"], f"特定测试: {test_path}"
    )


def run_fast_tests():
    """运行快速测试（跳过慢速测试）"""
    print("⚡ 运行快速测试...")
    return run_command(
        [sys.executable, "-m", "pytest", "tests/", "-m", "not slow", "-v"], "快速测试"
    )


def run_integration_tests():
    """运行集成测试"""
    print("🔗 运行集成测试...")
    return run_command(
        [sys.executable, "-m", "pytest", "tests/", "-m", "integration", "-v"], "集成测试"
    )


def check_code_quality():
    """检查代码质量"""
    print("🔍 检查代码质量...")

    # 运行flake8
    flake8_success = run_command(
        [sys.executable, "-m", "flake8", "app/", "tests/", "--max-line-length=120"],
        "代码风格检查 (flake8)",
    )

    # 运行black检查（不抛出异常）
    print(f"\n{'='*50}")
    print("运行: 代码格式化检查 (black)")
    print(f"命令: {sys.executable} -m black --check app/ tests/")
    print("=" * 50)
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "black", "--check", "app/", "tests/"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            print("✅ 成功!")
            if result.stdout:
                print(result.stdout)
            black_success = True
        else:
            print("❌ 失败!")
            print(f"错误代码: {result.returncode}")
            if result.stdout:
                print("标准输出:")
                print(result.stdout)
            if result.stderr:
                print("错误输出:")
                print(result.stderr)
            black_success = False
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        black_success = False

    # 运行isort检查
    isort_success = run_command(
        [sys.executable, "-m", "isort", "--check-only", "app/", "tests/"],
        "导入排序检查 (isort)",
    )

    # 运行mypy类型检查
    mypy_success = run_command(
        [sys.executable, "-m", "mypy", "app/", "--ignore-missing-imports"],
        "类型检查 (mypy)",
    )

    return all([flake8_success, black_success, isort_success, mypy_success])


def format_code():
    """格式化代码"""
    print("🎨 格式化代码...")

    # 运行black格式化
    black_success = run_command(
        [sys.executable, "-m", "black", "app/", "tests/"], "代码格式化 (black)"
    )

    # 运行isort排序导入
    isort_success = run_command(
        [sys.executable, "-m", "isort", "app/", "tests/"], "导入排序 (isort)"
    )

    return all([black_success, isort_success])


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="测试运行脚本")
    parser.add_argument("--install-deps", action="store_true", help="安装测试依赖")
    parser.add_argument("--unit", action="store_true", help="运行单元测试")
    parser.add_argument("--api", action="store_true", help="运行API测试")
    parser.add_argument("--models", action="store_true", help="运行模型测试")
    parser.add_argument("--core", action="store_true", help="运行核心功能测试")
    parser.add_argument("--all", action="store_true", help="运行所有测试")
    parser.add_argument("--coverage", action="store_true", help="运行测试并生成覆盖率报告")
    parser.add_argument("--html", action="store_true", help="运行测试并生成HTML报告")
    parser.add_argument("--fast", action="store_true", help="运行快速测试")
    parser.add_argument("--integration", action="store_true", help="运行集成测试")
    parser.add_argument("--test", type=str, help="运行特定测试文件或函数")
    parser.add_argument("--quality", action="store_true", help="检查代码质量")
    parser.add_argument("--format", action="store_true", help="格式化代码")
    parser.add_argument(
        "--full", action="store_true", help="完整测试流程（安装依赖、格式化、质量检查、测试、覆盖率）"
    )

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        return

    success = True

    if args.install_deps:
        success &= install_test_deps()

    if args.format:
        success &= format_code()

    if args.quality:
        success &= check_code_quality()

    if args.unit:
        success &= run_unit_tests()

    if args.api:
        success &= run_api_tests()

    if args.models:
        success &= run_model_tests()

    if args.core:
        success &= run_core_tests()

    if args.all:
        success &= run_all_tests()

    if args.coverage:
        success &= run_tests_with_coverage()

    if args.html:
        success &= run_tests_with_html_report()

    if args.fast:
        success &= run_fast_tests()

    if args.integration:
        success &= run_integration_tests()

    if args.test:
        success &= run_specific_test(args.test)

    if args.full:
        print("🔄 开始完整测试流程...")
        success &= install_test_deps()
        success &= format_code()
        success &= check_code_quality()
        success &= run_all_tests()
        success &= run_tests_with_coverage()

    print(f"\n{'='*50}")
    if success:
        print("🎉 所有操作成功完成!")
    else:
        print("❌ 部分操作失败，请检查错误信息")
        sys.exit(1)
    print("=" * 50)


if __name__ == "__main__":
    main()
