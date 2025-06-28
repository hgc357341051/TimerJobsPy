#!/usr/bin/env python3
"""
Linux兼容性测试脚本
测试CLI在Linux环境下的基本功能
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def test_platform_info():
    """测试平台信息"""
    print(f"操作系统: {platform.system()}")
    print(f"平台版本: {platform.release()}")
    print(f"Python版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")

def test_path_handling():
    """测试路径处理"""
    print("\n=== 路径处理测试 ===")
    pid_dir = Path("runtime")
    print(f"PID目录: {pid_dir}")
    print(f"PID目录绝对路径: {pid_dir.absolute()}")
    print(f"PID目录是否存在: {pid_dir.exists()}")

def test_process_management():
    """测试进程管理"""
    print("\n=== 进程管理测试 ===")
    if platform.system() == "Windows":
        print("Windows环境 - 使用tasklist检查进程")
        try:
            result = subprocess.run(["tasklist"], capture_output=True, text=True)
            print(f"tasklist命令可用: {result.returncode == 0}")
        except FileNotFoundError:
            print("tasklist命令不可用")
    else:
        print("Unix/Linux环境 - 使用信号检查进程")
        try:
            # 测试信号0（检查进程是否存在）
            os.kill(os.getpid(), 0)
            print("信号0检查可用")
        except OSError:
            print("信号0检查失败")

def test_subprocess():
    """测试子进程创建"""
    print("\n=== 子进程测试 ===")
    try:
        if platform.system() == "Windows":
            process = subprocess.Popen(
                [sys.executable, "-c", "print('Windows子进程测试')"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        else:
            process = subprocess.Popen(
                [sys.executable, "-c", "print('Linux子进程测试')"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid,
            )
        
        stdout, stderr = process.communicate()
        print(f"子进程输出: {stdout.decode('utf-8').strip()}")
        print(f"子进程返回码: {process.returncode}")
    except Exception as e:
        print(f"子进程测试失败: {e}")

def test_signal_handling():
    """测试信号处理"""
    print("\n=== 信号处理测试 ===")
    if platform.system() != "Windows":
        try:
            import signal
            print(f"SIGTERM: {signal.SIGTERM}")
            print(f"SIGKILL: {signal.SIGKILL}")
            print("信号处理可用")
        except ImportError:
            print("信号模块不可用")
    else:
        print("Windows环境 - 跳过信号测试")

def main():
    """主测试函数"""
    print("Linux兼容性测试")
    print("=" * 50)
    
    test_platform_info()
    test_path_handling()
    test_process_management()
    test_subprocess()
    test_signal_handling()
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    main() 