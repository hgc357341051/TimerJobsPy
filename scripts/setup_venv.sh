#!/bin/bash

# 自动生成Python虚拟环境脚本
# 支持Linux/macOS系统

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${BLUE}🚀 $1${NC}"
}

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_NAME="venv"
VENV_PATH="$PROJECT_ROOT/$VENV_NAME"

print_header "自动生成Python虚拟环境脚本"
echo "=========================================="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    print_error "未找到Python3，请先安装Python 3.8+"
    exit 1
fi

# 检查Python版本
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

print_info "当前Python版本: $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "需要Python 3.8或更高版本"
    exit 1
fi

print_success "Python版本检查通过"

# 切换到项目根目录
cd "$PROJECT_ROOT"
print_info "项目根目录: $PROJECT_ROOT"

# 检查虚拟环境是否已存在
if [ -d "$VENV_PATH" ]; then
    print_warning "虚拟环境 '$VENV_NAME' 已存在"
    read -p "是否删除现有环境并重新创建? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "删除现有虚拟环境..."
        rm -rf "$VENV_PATH"
    else
        print_info "使用现有虚拟环境"
        goto_activate_venv
    fi
fi

# 创建虚拟环境
print_info "创建虚拟环境: $VENV_PATH"
python3 -m venv "$VENV_PATH"
if [ $? -ne 0 ]; then
    print_error "创建虚拟环境失败"
    exit 1
fi
print_success "虚拟环境创建成功"

# 激活虚拟环境并升级pip
print_info "升级pip..."
source "$VENV_PATH/bin/activate"
python -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    print_error "pip升级失败"
    exit 1
fi
print_success "pip升级成功"

# 安装主依赖
print_info "安装主依赖包..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        print_error "主依赖安装失败"
        exit 1
    fi
    print_success "主依赖安装成功"
else
    print_warning "requirements.txt 文件不存在"
fi

# 询问是否安装测试依赖
read -p "是否安装测试依赖? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "安装测试依赖包..."
    if [ -f "requirements-test.txt" ]; then
        pip install -r requirements-test.txt
        if [ $? -ne 0 ]; then
            print_warning "测试依赖安装失败，但主依赖已安装"
        else
            print_success "测试依赖安装成功"
        fi
    else
        print_warning "requirements-test.txt 文件不存在"
    fi
fi

goto_activate_venv() {
    echo
    echo "=========================================="
    print_success "虚拟环境设置完成!"
    echo "=========================================="
    echo
    echo "📋 激活虚拟环境:"
    echo "   source $VENV_PATH/bin/activate"
    echo
    echo "📁 虚拟环境位置: $VENV_PATH"
    echo "🐍 Python解释器: $VENV_PATH/bin/python"
    echo
    echo "💡 提示:"
    echo "   - 激活后可以使用 'deactivate' 退出虚拟环境"
    echo "   - 使用 'pip list' 查看已安装的包"
    echo "   - 使用 'python -m pytest' 运行测试"
    echo "=========================================="
    echo
    echo "🔗 现在可以运行以下命令激活虚拟环境:"
    echo "   source $VENV_PATH/bin/activate"
    echo
}

goto_activate_venv 