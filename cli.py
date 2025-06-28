#!/usr/bin/env python3
"""
小胡定时任务系统（Python版）命令行接口
支持前台模式、后台模式、守护进程模式启动
跨平台兼容：Windows/Linux/macOS
"""

import os
import sys
import time
import signal
import subprocess
import argparse
import platform
import json
from pathlib import Path
from typing import Optional, List
import uvicorn
from uvicorn.config import Config as UvicornConfig
from uvicorn.server import Server

from app.config import Config


def check_python_version():
    """检查Python版本兼容性"""
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        print("请升级Python版本后重试")
        sys.exit(1)

    # 显示版本信息
    version_info = f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 11):
        print(f"OK {version_info} (推荐版本)")
    elif sys.version_info >= (3, 10):
        print(f"OK {version_info} (最佳版本)")
    elif sys.version_info >= (3, 9):
        print(f"OK {version_info} (推荐版本)")
    else:
        print(f"WARN {version_info} (最低支持版本)")


class PyJobsCLI:
    """PyJobs命令行接口类"""

    def __init__(self):
        self.app_name = "pyjobs"
        self.pid_dir = Path("runtime")
        self.job_pid_file = self.pid_dir / "job.pid"
        self.daemon_pid_file = self.pid_dir / "daemon.pid"
        self.config_file = Path("app/config.py")

        # 确保PID目录存在
        self.pid_dir.mkdir(exist_ok=True)

    def main(self):
        """主入口函数"""
        # 检查Python版本
        check_python_version()

        parser = argparse.ArgumentParser(
            description="小胡定时任务系统（Python版）",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
使用示例:
  python cli.py start              # 前台模式运行
  python cli.py start -d           # 后台模式运行
  python cli.py start -f           # 守护进程模式运行
  python cli.py start -d -f        # 后台+守护进程模式运行
  python cli.py stop               # 停止后台进程
  python cli.py stop -f            # 停止守护进程
  python cli.py status             # 查看运行状态
  python cli.py daemon             # 进入守护模式
            """,
        )

        parser.add_argument(
            "command",
            choices=["start", "stop", "status", "daemon", "restart", "reload"],
            help="执行命令",
        )
        parser.add_argument("-d", "--daemon", action="store_true", help="后台模式运行")
        parser.add_argument("-f", "--foreground", action="store_true", help="守护进程模式运行")
        parser.add_argument(
            "-p", "--port", type=int, default=Config.SERVER_PORT, help=f"服务端口 (默认: {Config.SERVER_PORT})"
        )
        parser.add_argument(
            "-H", "--host", default=Config.SERVER_HOST, help=f"服务地址 (默认: {Config.SERVER_HOST})"
        )
        parser.add_argument("--reload", action="store_true", help="开发模式热重载")

        args = parser.parse_args()

        try:
            if args.command == "start":
                self.handle_start(args)
            elif args.command == "stop":
                self.handle_stop(args)
            elif args.command == "status":
                self.handle_status()
            elif args.command == "daemon":
                self.handle_daemon()
            elif args.command == "restart":
                self.handle_restart(args)
            elif args.command == "reload":
                self.handle_reload()
        except KeyboardInterrupt:
            print("\n操作被用户中断")
            sys.exit(1)
        except Exception as e:
            print(f"错误: {e}")
            sys.exit(1)

    def handle_start(self, args):
        """处理启动命令"""
        if args.daemon and args.foreground:
            # 后台+守护进程模式
            print("启动后台+守护进程模式...")
            self.start_daemon_mode(args)
        elif args.foreground:
            # 守护进程模式（前台守护）
            print("启动守护进程模式...")
            self.start_foreground_daemon_mode(args)
        elif args.daemon:
            # 后台模式
            print("启动后台模式...")
            self.start_background_mode(args)
        else:
            # 前台模式
            print("启动前台模式...")
            self.start_foreground_mode(args)

    def handle_stop(self, args):
        """处理停止命令"""
        if args.foreground:
            # 停止守护进程模式
            print("停止守护进程模式...")
            self.stop_daemon_mode()
        else:
            # 停止后台模式
            print("停止后台模式...")
            self.stop_background_mode()

    def handle_status(self):
        """处理状态查询命令"""
        if self.is_running():
            pid = self.read_job_pid()
            print(f"系统正在运行，PID: {pid}")
        else:
            print("系统未运行")

    def handle_daemon(self):
        """处理守护进程命令"""
        print("进入守护进程模式...")
        self.daemon_loop()

    def handle_restart(self, args):
        """处理重启命令"""
        print("重启系统...")
        self.stop_background_mode()
        time.sleep(2)
        self.handle_start(args)

    def handle_reload(self):
        """处理重载命令"""
        print("重载配置...")
        # 发送重载信号给运行中的进程
        pid = self.read_job_pid()
        if pid and self.is_process_running(pid):
            if platform.system() == "Windows":
                # Windows下发送信号
                os.kill(pid, signal.SIGTERM)
            else:
                # Unix系统发送USR1信号
                os.kill(pid, signal.SIGUSR1)
            print(f"已发送重载信号给进程 {pid}")
        else:
            print("未找到运行中的进程")

    def start_foreground_mode(self, args):
        """前台模式启动"""
        try:
            print(f"启动服务器: {args.host}:{args.port}")
            config = UvicornConfig(
                "app.main:app",
                host=args.host,
                port=args.port,
                reload=args.reload,
                log_level="info",
                access_log=False,
            )
            server = Server(config=config)
            server.run()
        except Exception as e:
            print(f"启动失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def start_background_mode(self, args):
        """后台模式启动"""
        if self.is_running():
            print("系统已在后台运行")
            return

        # 构建启动命令
        cmd = [sys.executable, "cli.py", "start", "-H", args.host, "-p", str(args.port)]
        if args.reload:
            cmd.append("--reload")

        print(f"启动命令: {' '.join(cmd)}")

        # 启动后台进程
        if platform.system() == "Windows":
            # Windows后台启动
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            process = subprocess.Popen(
                cmd,
                startupinfo=startupinfo,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        else:
            # Unix/Linux后台启动 - 使用进程组
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid,  # 创建新的进程组
            )

        # 等待一小段时间检查进程是否正常启动
        time.sleep(2)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            # 进程还在运行
            self.write_job_pid(process.pid)
            print(f"系统已在后台启动，PID: {process.pid}")
        else:
            # 进程已退出，获取错误信息
            stdout, stderr = process.communicate()
            print(f"后台进程启动失败，返回码: {process.returncode}")
            if stderr:
                print(f"错误信息: {stderr.decode('utf-8', errors='ignore')}")
            if stdout:
                print(f"输出信息: {stdout.decode('utf-8', errors='ignore')}")
            print("请检查应用配置和依赖是否正确")
            return

    def start_foreground_daemon_mode(self, args):
        """前台守护进程模式启动"""
        print("启动前台守护进程模式...")
        self.write_daemon_pid(os.getpid())
        
        try:
            # 直接启动守护进程循环
            self.daemon_loop()
        except KeyboardInterrupt:
            print("\n前台守护进程被中断")
        finally:
            self.remove_daemon_pid()

    def start_daemon_mode(self, args):
        """守护进程模式启动"""
        if self.is_running():
            print("系统已在守护进程模式下运行")
            return

        # 构建守护进程启动命令
        cmd = [
            sys.executable,
            "cli.py",
            "daemon",
            "-H",
            args.host,
            "-p",
            str(args.port),
        ]
        if args.reload:
            cmd.append("--reload")

        # 启动守护进程
        if platform.system() == "Windows":
            # Windows守护进程启动
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            process = subprocess.Popen(
                cmd,
                startupinfo=startupinfo,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        else:
            # Unix守护进程启动
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid,
            )

        print(f"守护进程已启动，PID: {process.pid}")

    def stop_background_mode(self):
        """停止后台模式"""
        pid = self.read_job_pid()
        if not pid:
            print("未找到运行中的进程")
            return

        # 检查进程是否真的在运行
        if not self.is_process_running(pid):
            print(f"进程 {pid} 已不存在，清理PID文件")
            self.remove_job_pid()
            return

        if self.kill_process(pid):
            self.remove_job_pid()
            print(f"已停止进程 PID: {pid}")
        else:
            print(f"停止进程失败 PID: {pid}")
            # 即使停止失败，也清理PID文件
            self.remove_job_pid()

    def stop_daemon_mode(self):
        """停止守护进程模式"""
        # 停止业务进程
        job_pid = self.read_job_pid()
        if job_pid:
            self.kill_process(job_pid)
            self.remove_job_pid()

        # 停止守护进程
        daemon_pid = self.read_daemon_pid()
        if daemon_pid:
            self.kill_process(daemon_pid)
            self.remove_daemon_pid()

        print("已优雅停止守护进程和业务进程")

    def daemon_loop(self):
        """守护进程主循环"""
        self.write_daemon_pid(os.getpid())

        max_restarts = 100
        restart_delay = 3
        restarts = 0

        while restarts < max_restarts:
            try:
                print(f"[守护] 启动业务子进程... (第{restarts + 1}次)")

                # 启动业务进程
                cmd = [sys.executable, "cli.py", "start"]
                process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )

                pid = process.pid
                self.write_job_pid(pid)
                print(f"[守护] 子进程PID: {pid}")

                # 等待进程结束
                stdout, stderr = process.communicate()

                self.remove_job_pid()

                if process.returncode == 0:
                    print("[守护] 子进程正常退出")
                else:
                    print(f"[守护] 子进程异常退出，返回码: {process.returncode}")
                    if stderr:
                        print(f"[守护] 错误输出: {stderr}")

                restarts += 1

                if restarts >= max_restarts:
                    print("[守护] 达到最大重启次数，守护进程退出")
                    break

                print(f"[守护] {restart_delay} 秒后重启子进程...")
                time.sleep(restart_delay)

            except KeyboardInterrupt:
                print("[守护] 收到中断信号，退出守护进程")
                break
            except Exception as e:
                print(f"[守护] 启动子进程失败: {e}")
                time.sleep(restart_delay)
                restarts += 1

        self.remove_daemon_pid()

    def is_running(self) -> bool:
        """检查系统是否正在运行"""
        pid = self.read_job_pid()
        if not pid:
            return False
        return self.is_process_running(pid)

    def is_process_running(self, pid: int) -> bool:
        """检查指定PID的进程是否运行"""
        try:
            if platform.system() == "Windows":
                # Windows检查进程
                result = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True
                )
                return str(pid) in result.stdout
            else:
                # Unix/Linux检查进程 - 发送信号0
                os.kill(pid, 0)
                return True
        except (OSError, subprocess.SubprocessError):
            return False

    def kill_process(self, pid: int) -> bool:
        """杀死指定PID的进程"""
        try:
            if platform.system() == "Windows":
                # Windows优雅关闭
                result = subprocess.run(
                    ["taskkill", "/PID", str(pid)], capture_output=True, text=True
                )
                if result.returncode != 0:
                    # 如果失败再强杀
                    result = subprocess.run(
                        ["taskkill", "/PID", str(pid), "/F"],
                        capture_output=True,
                        text=True,
                    )
                return result.returncode == 0
            else:
                # Unix/Linux优雅关闭
                os.kill(pid, signal.SIGTERM)
                time.sleep(2)

                # 检查是否还在运行，如果还在就强杀
                if self.is_process_running(pid):
                    os.kill(pid, signal.SIGKILL)
                    time.sleep(1)

                return True
        except OSError:
            return False

    def write_job_pid(self, pid: int):
        """写入业务进程PID"""
        try:
            self.job_pid_file.write_text(str(pid))
        except Exception as e:
            print(f"写入PID文件失败: {e}")

    def read_job_pid(self) -> Optional[int]:
        """读取业务进程PID"""
        try:
            if self.job_pid_file.exists():
                return int(self.job_pid_file.read_text().strip())
        except (ValueError, IOError):
            pass
        return None

    def remove_job_pid(self):
        """删除业务进程PID文件"""
        try:
            self.job_pid_file.unlink(missing_ok=True)
        except Exception:
            pass

    def write_daemon_pid(self, pid: int):
        """写入守护进程PID"""
        try:
            self.daemon_pid_file.write_text(str(pid))
        except Exception as e:
            print(f"写入守护进程PID文件失败: {e}")

    def read_daemon_pid(self) -> Optional[int]:
        """读取守护进程PID"""
        try:
            if self.daemon_pid_file.exists():
                return int(self.daemon_pid_file.read_text().strip())
        except (ValueError, IOError):
            pass
        return None

    def remove_daemon_pid(self):
        """删除守护进程PID文件"""
        try:
            self.daemon_pid_file.unlink(missing_ok=True)
        except Exception:
            pass


def main():
    """主函数"""
    cli = PyJobsCLI()
    cli.main()


if __name__ == "__main__":
    main()
