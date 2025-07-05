#!/usr/bin/env python3
"""
自动生成Python虚拟环境脚本
支持Windows和Unix系统
"""

import os
import sys
import subprocess
import platform
import argparse
from pathlib import Path


class VenvSetup:
    def __init__(self, venv_name="venv", python_version=None):
        self.venv_name = venv_name
        self.python_version = python_version
        self.project_root = Path(__file__).parent.parent
        self.venv_path = self.project_root / venv_name
        
    def check_python_version(self):
        """检查Python版本"""
        version = sys.version_info
        print(f"当前Python版本: {version.major}.{version.minor}.{version.micro}")
        
        if version < (3, 8):
            print("❌ 错误: 需要Python 3.8或更高版本")
            return False
        
        if self.python_version:
            required_major, required_minor = map(int, self.python_version.split('.'))
            if version.major != required_major or version.minor < required_minor:
                print(f"❌ 错误: 需要Python {self.python_version}或更高版本")
                return False
        
        print("✅ Python版本检查通过")
        return True
    
    def create_venv(self):
        """创建虚拟环境"""
        if self.venv_path.exists():
            print(f"⚠️  虚拟环境 '{self.venv_name}' 已存在")
            response = input("是否删除现有环境并重新创建? (y/N): ").strip().lower()
            if response == 'y':
                self.remove_venv()
            else:
                print("使用现有虚拟环境")
                return True
        
        print(f"🔧 创建虚拟环境: {self.venv_path}")
        
        try:
            subprocess.run([
                sys.executable, "-m", "venv", str(self.venv_path)
            ], check=True, capture_output=True, text=True)
            print("✅ 虚拟环境创建成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 创建虚拟环境失败: {e}")
            return False
    
    def remove_venv(self):
        """删除虚拟环境"""
        if self.venv_path.exists():
            print(f"🗑️  删除现有虚拟环境: {self.venv_path}")
            import shutil
            shutil.rmtree(self.venv_path)
    
    def get_pip_path(self):
        """获取pip路径"""
        if platform.system() == "Windows":
            return self.venv_path / "Scripts" / "pip.exe"
        else:
            return self.venv_path / "bin" / "pip"
    
    def get_activate_script(self):
        """获取激活脚本路径"""
        if platform.system() == "Windows":
            return self.venv_path / "Scripts" / "activate.bat"
        else:
            return self.venv_path / "bin" / "activate"
    
    def upgrade_pip(self):
        """升级pip"""
        pip_path = self.get_pip_path()
        print("📦 升级pip...")
        
        try:
            subprocess.run([
                str(pip_path), "install", "--upgrade", "pip"
            ], check=True, capture_output=True, text=True)
            print("✅ pip升级成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ pip升级失败: {e}")
            return False
    
    def install_requirements(self, requirements_file):
        """安装依赖包"""
        pip_path = self.get_pip_path()
        req_file = self.project_root / requirements_file
        
        if not req_file.exists():
            print(f"⚠️  依赖文件不存在: {req_file}")
            return False
        
        print(f"📦 安装依赖包: {requirements_file}")
        
        try:
            subprocess.run([
                str(pip_path), "install", "-r", str(req_file)
            ], check=True, capture_output=True, text=True)
            print(f"✅ {requirements_file} 安装成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 安装依赖失败: {e}")
            return False
    
    def show_activation_instructions(self):
        """显示激活说明"""
        activate_script = self.get_activate_script()
        
        print("\n" + "="*60)
        print("🎉 虚拟环境设置完成!")
        print("="*60)
        
        if platform.system() == "Windows":
            print(f"\n📋 激活虚拟环境:")
            print(f"   {activate_script}")
            print(f"   或者运行: {self.venv_name}\\Scripts\\activate")
        else:
            print(f"\n📋 激活虚拟环境:")
            print(f"   source {activate_script}")
            print(f"   或者运行: source {self.venv_name}/bin/activate")
        
        print(f"\n📁 虚拟环境位置: {self.venv_path}")
        print(f"🐍 Python解释器: {self.venv_path / ('Scripts' if platform.system() == 'Windows' else 'bin') / 'python.exe'}")
        
        print("\n💡 提示:")
        print("   - 激活后可以使用 'deactivate' 退出虚拟环境")
        print("   - 使用 'pip list' 查看已安装的包")
        print("   - 使用 'python -m pytest' 运行测试")
        print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description="自动生成Python虚拟环境",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python scripts/setup_venv.py                    # 基本使用
  python scripts/setup_venv.py --install-test     # 安装测试依赖
  python scripts/setup_venv.py --force            # 强制重新创建
  python scripts/setup_venv.py --venv-name myenv  # 自定义环境名称
        """
    )
    parser.add_argument("--venv-name", default="venv", help="虚拟环境名称 (默认: venv)")
    parser.add_argument("--python-version", help="指定Python版本 (例如: 3.8)")
    parser.add_argument("--requirements", default="requirements.txt", help="依赖文件 (默认: requirements.txt)")
    parser.add_argument("--test-requirements", default="requirements-test.txt", help="测试依赖文件 (默认: requirements-test.txt)")
    parser.add_argument("--install-test", action="store_true", help="同时安装测试依赖")
    parser.add_argument("--force", action="store_true", help="强制重新创建虚拟环境")
    
    args = parser.parse_args()
    
    setup = VenvSetup(args.venv_name, args.python_version)
    
    print("🚀 开始设置Python虚拟环境...")
    print(f"📁 项目根目录: {setup.project_root}")
    print(f"🐍 虚拟环境名称: {setup.venv_name}")
    
    # 检查Python版本
    if not setup.check_python_version():
        sys.exit(1)
    
    # 强制重新创建
    if args.force and setup.venv_path.exists():
        setup.remove_venv()
    
    # 创建虚拟环境
    if not setup.create_venv():
        sys.exit(1)
    
    # 升级pip
    if not setup.upgrade_pip():
        sys.exit(1)
    
    # 安装主依赖
    if not setup.install_requirements(args.requirements):
        sys.exit(1)
    
    # 安装测试依赖
    if args.install_test:
        if not setup.install_requirements(args.test_requirements):
            print("⚠️  测试依赖安装失败，但主依赖已安装")
    
    # 显示激活说明
    setup.show_activation_instructions()


if __name__ == "__main__":
    main() 