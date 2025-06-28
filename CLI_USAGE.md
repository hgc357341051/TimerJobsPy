# 小胡定时任务系统（Python版）命令行接口使用说明

## 概述

Python重构版完全实现了Go原版的命令式启动功能，支持前台模式、后台模式、守护进程模式等多种启动方式，并提供了丰富的进程管理功能。

## 启动方式对比

| 功能 | Go版本 | Python版本 | 说明 |
|------|--------|------------|------|
| 前台模式 | `./jobs start` | `python cli.py start` | 完全兼容 |
| 后台模式 | `./jobs start -d` | `python cli.py start -d` | 完全兼容 |
| 守护进程模式 | `./jobs start -d -f` | `python cli.py start -d -f` | 完全兼容 |
| 停止后台 | `./jobs stop` | `python cli.py stop` | 完全兼容 |
| 停止守护进程 | `./jobs stop -f` | `python cli.py stop -f` | 完全兼容 |
| 状态查询 | `./jobs status` | `python cli.py status` | 完全兼容 |
| 守护进程 | `./jobs daemon` | `python cli.py daemon` | 完全兼容 |

## 命令行接口（CLI）

### 基本命令

```bash
# 前台模式启动（开发调试）
python cli.py start

# 后台模式启动（生产环境）
python cli.py start -d

# 守护进程模式启动（高可用）
python cli.py start -d -f

# 停止后台模式
python cli.py stop

# 停止守护进程模式
python cli.py stop -f

# 查看运行状态
python cli.py status

# 进入守护模式
python cli.py daemon

# 重启服务
python cli.py restart

# 重载配置
python cli.py reload
```

### 高级选项

```bash
# 指定端口启动
python cli.py start -p 8080

# 指定主机启动
python cli.py start -H 127.0.0.1

# 开发模式热重载
python cli.py start --reload

# 组合使用
python cli.py start -d -p 8080 -H 0.0.0.0
```

## Makefile 构建工具

### 基本命令

```bash
# 查看所有可用命令
make help

# 安装依赖
make install

# 构建项目
make build

# 清理构建文件
make clean
```

### 启动和停止

```bash
# 前台模式运行
make start

# 后台模式运行
make start-bg

# 守护进程模式运行
make start-daemon

# 停止后台模式
make stop

# 停止守护进程模式
make stop-all

# 查看运行状态
make status

# 重启服务
make restart

# 重载配置
make reload
```

### 开发工具

```bash
# 开发模式（热重载）
make dev

# 代码格式化
make fmt

# 代码检查
make lint

# 类型检查
make type-check

# 运行测试
make test

# 安全扫描
make security-scan
```

### 数据库管理

```bash
# 初始化数据库
make init-db

# 数据库迁移
make migrate

# 生成迁移文件
make migrate-create

# 备份数据库
make backup-db
```

### 部署工具

```bash
# 构建Docker镜像
make docker

# 创建发布包
make release

# 安装系统服务（Linux）
sudo make install-service

# 卸载系统服务（Linux）
sudo make uninstall-service
```

## 启动脚本

### Linux/macOS 启动脚本

```bash
# 给脚本添加执行权限
chmod +x start.sh

# 前台模式启动
./start.sh start

# 后台模式启动
./start.sh start-bg

# 守护进程模式启动
./start.sh start-daemon

# 停止服务
./start.sh stop

# 停止所有进程
./start.sh stop-all

# 查看状态
./start.sh status

# 重启服务
./start.sh restart

# 重载配置
./start.sh reload

# 查看帮助
./start.sh help
```

### Windows 启动脚本

```cmd
# 前台模式启动
start.bat start

# 后台模式启动
start.bat start-bg

# 守护进程模式启动
start.bat start-daemon

# 停止服务
start.bat stop

# 停止所有进程
start.bat stop-all

# 查看状态
start.bat status

# 重启服务
start.bat restart

# 重载配置
start.bat reload

# 查看帮助
start.bat help
```

## 进程管理机制

### PID文件管理

- **业务进程PID**: `runtime/job.pid`
- **守护进程PID**: `runtime/daemon.pid`
- **自动创建**: 启动时自动创建PID文件
- **自动清理**: 停止时自动删除PID文件

### 进程检查机制

- **Windows**: 使用 `tasklist` 命令检查进程
- **Unix/Linux**: 使用 `kill(pid, 0)` 检查进程
- **跨平台兼容**: 自动识别操作系统

### 优雅关闭机制

- **Windows**: 先尝试 `taskkill /PID`，失败后使用 `taskkill /PID /F`
- **Unix/Linux**: 先发送 `SIGTERM`，失败后发送 `SIGKILL`
- **超时保护**: 2秒超时后强制关闭

## 守护进程机制

### 守护进程功能

- **自动重启**: 业务进程异常退出时自动重启
- **最大重启次数**: 防止无限重启（默认100次）
- **重启间隔**: 3秒重启间隔，避免频繁重启
- **日志记录**: 详细记录重启过程和原因

### 守护进程循环

```python
def daemon_loop(self):
    """守护进程主循环"""
    max_restarts = 100
    restart_delay = 3
    restarts = 0
    
    while restarts < max_restarts:
        # 启动业务进程
        process = subprocess.Popen([...])
        
        # 等待进程结束
        process.communicate()
        
        # 检查退出状态
        if process.returncode != 0:
            print(f"[守护] 子进程异常退出，返回码: {process.returncode}")
        
        # 重启计数
        restarts += 1
        
        # 延迟重启
        time.sleep(restart_delay)
```

## 系统服务管理

### systemd 服务文件

```ini
[Unit]
Description=小胡定时任务系统（Python版）
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/pyjobs
Environment=PATH=/opt/pyjobs/venv/bin
ExecStart=/opt/pyjobs/venv/bin/python /opt/pyjobs/cli.py start -d -f
ExecReload=/bin/kill -HUP $MAINPID
ExecStop=/opt/pyjobs/venv/bin/python /opt/pyjobs/cli.py stop -f
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 服务管理命令

```bash
# 安装服务
sudo make install-service

# 启动服务
sudo systemctl start pyjobs

# 停止服务
sudo systemctl stop pyjobs

# 重启服务
sudo systemctl restart pyjobs

# 查看状态
sudo systemctl status pyjobs

# 查看日志
sudo journalctl -u pyjobs -f

# 设置开机自启
sudo systemctl enable pyjobs

# 禁用开机自启
sudo systemctl disable pyjobs

# 卸载服务
sudo make uninstall-service
```

## 配置热重载

### 重载机制

- **信号发送**: 通过 `SIGUSR1` 或 `SIGTERM` 发送重载信号
- **配置检查**: 自动检查配置文件变更
- **优雅重载**: 不中断服务的情况下重载配置
- **错误处理**: 重载失败时保持原配置

### 重载命令

```bash
# 通过CLI重载
python cli.py reload

# 通过Makefile重载
make reload

# 通过启动脚本重载
./start.sh reload

# 通过systemd重载
sudo systemctl reload pyjobs
```

## 日志管理

### 日志文件

- **系统日志**: 通过API `GET /jobs/zapLogs` 查看
- **任务日志**: 通过API `POST /jobs/logs` 查询
- **服务日志**: `sudo journalctl -u pyjobs -f`
- **文件日志**: 配置的日志文件路径

### 日志级别

- **DEBUG**: 调试信息
- **INFO**: 一般信息
- **WARNING**: 警告信息
- **ERROR**: 错误信息
- **CRITICAL**: 严重错误

## 性能优化

### 生产环境建议

1. **使用守护进程模式**: 确保高可用性
2. **配置MySQL数据库**: 提高性能和稳定性
3. **设置合适的日志级别**: 减少日志输出
4. **使用反向代理**: Nginx负载均衡
5. **定期清理日志**: 避免磁盘空间不足

### 监控建议

1. **进程监控**: 定期检查进程状态
2. **资源监控**: 监控CPU、内存、磁盘使用
3. **日志监控**: 监控错误日志和异常
4. **性能监控**: 监控API响应时间

## 故障排除

### 常见问题

1. **进程启动失败**
   - 检查Python环境
   - 检查依赖安装
   - 检查配置文件

2. **进程无法停止**
   - 检查PID文件
   - 手动杀死进程
   - 检查权限问题

3. **守护进程异常**
   - 检查业务进程日志
   - 检查重启次数
   - 检查系统资源

4. **配置重载失败**
   - 检查配置文件语法
   - 检查文件权限
   - 查看错误日志

### 调试命令

```bash
# 查看进程状态
ps aux | grep python

# 查看端口占用
netstat -tlnp | grep 8000

# 查看PID文件
cat runtime/job.pid
cat runtime/daemon.pid

# 查看系统日志
tail -f /var/log/syslog | grep pyjobs

# 查看服务日志
sudo journalctl -u pyjobs -f
```

## 总结

Python重构版完全实现了Go原版的所有命令式启动功能，并在此基础上提供了更丰富的工具和更好的用户体验：

1. **完全兼容**: 所有Go版本的命令都可以在Python版本中找到对应
2. **功能增强**: 提供了Makefile、启动脚本等额外工具
3. **跨平台**: 支持Windows、Linux、macOS
4. **易用性**: 提供了详细的帮助信息和错误提示
5. **可维护性**: 代码结构清晰，易于扩展和维护

用户可以根据自己的需求选择合适的启动方式，从简单的开发调试到复杂的高可用生产环境部署。

## 环境要求

### Python版本
- **最低要求**: Python 3.8+
- **推荐版本**: Python 3.10 或 3.11
- **最佳版本**: Python 3.11+

### 版本检查
在开始使用前，建议检查Python版本：

```bash
# 使用检查脚本
python check_version.py

# 或使用Makefile
make check-version

# 或手动检查
python --version
```

## 基本命令 