#!/bin/bash
# 小胡定时任务系统（Python版）启动脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 显示帮助信息
show_help() {
    echo -e "${BLUE}小胡定时任务系统（Python版）启动脚本${NC}"
    echo ""
    echo "用法: $0 [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  start          启动服务（前台模式）"
    echo "  start-bg       启动服务（后台模式）"
    echo "  start-daemon   启动服务（守护进程模式）"
    echo "  stop           停止服务"
    echo "  stop-all       停止所有相关进程"
    echo "  restart        重启服务"
    echo "  status         查看服务状态"
    echo "  reload         重载配置"
    echo "  help           显示此帮助信息"
    echo ""
    echo "选项:"
    echo "  -p, --port     指定端口（默认: 8000）"
    echo "  -H, --host     指定主机（默认: 0.0.0.0）"
    echo "  --reload       开发模式热重载"
    echo ""
    echo "示例:"
    echo "  $0 start                    # 前台模式启动"
    echo "  $0 start-bg                 # 后台模式启动"
    echo "  $0 start-daemon             # 守护进程模式启动"
    echo "  $0 stop                     # 停止服务"
    echo "  $0 status                   # 查看状态"
    echo "  $0 start -p 8080            # 指定端口启动"
    echo "  $0 start --reload           # 开发模式启动"
}

# 检查Python环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}错误: 未找到 python3${NC}"
        echo "请安装 Python 3.8 或更高版本"
        exit 1
    fi
    
    # 检查虚拟环境
    if [ -d "venv" ]; then
        echo -e "${YELLOW}检测到虚拟环境，正在激活...${NC}"
        source venv/bin/activate
    fi
}

# 检查依赖
check_dependencies() {
    if [ ! -f "requirements.txt" ]; then
        echo -e "${RED}错误: 未找到 requirements.txt${NC}"
        exit 1
    fi
    
    if [ ! -f "cli.py" ]; then
        echo -e "${RED}错误: 未找到 cli.py${NC}"
        exit 1
    fi
}

# 启动服务
start_service() {
    local mode="$1"
    shift
    
    echo -e "${GREEN}启动小胡定时任务系统...${NC}"
    echo -e "${BLUE}模式: $mode${NC}"
    
    # 构建命令
    local cmd="python3 cli.py start"
    
    case "$mode" in
        "foreground")
            cmd="python3 cli.py start"
            ;;
        "background")
            cmd="python3 cli.py start -d"
            ;;
        "daemon")
            cmd="python3 cli.py start -d -f"
            ;;
    esac
    
    # 添加额外参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--port)
                cmd="$cmd -p $2"
                shift 2
                ;;
            -H|--host)
                cmd="$cmd -H $2"
                shift 2
                ;;
            --reload)
                cmd="$cmd --reload"
                shift
                ;;
            *)
                echo -e "${RED}未知选项: $1${NC}"
                exit 1
                ;;
        esac
    done
    
    echo -e "${BLUE}执行命令: $cmd${NC}"
    eval $cmd
}

# 停止服务
stop_service() {
    local mode="$1"
    
    case "$mode" in
        "normal")
            echo -e "${YELLOW}停止服务...${NC}"
            python3 cli.py stop
            ;;
        "all")
            echo -e "${YELLOW}停止所有相关进程...${NC}"
            python3 cli.py stop -f
            ;;
    esac
}

# 查看状态
show_status() {
    echo -e "${BLUE}查看服务状态...${NC}"
    python3 cli.py status
}

# 重启服务
restart_service() {
    echo -e "${YELLOW}重启服务...${NC}"
    python3 cli.py restart
}

# 重载配置
reload_config() {
    echo -e "${YELLOW}重载配置...${NC}"
    python3 cli.py reload
}

# 主函数
main() {
    # 检查环境
    check_python
    check_dependencies
    
    # 解析命令
    case "${1:-help}" in
        start)
            shift
            start_service "foreground" "$@"
            ;;
        start-bg)
            shift
            start_service "background" "$@"
            ;;
        start-daemon)
            shift
            start_service "daemon" "$@"
            ;;
        stop)
            stop_service "normal"
            ;;
        stop-all)
            stop_service "all"
            ;;
        restart)
            restart_service
            ;;
        status)
            show_status
            ;;
        reload)
            reload_config
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}未知命令: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 