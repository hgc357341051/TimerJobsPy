# 小胡定时任务系统（Python重构版）

一个高可用、可扩展、支持多种执行模式的企业级定时任务管理系统，适用于自动化运维、定时数据处理、批量任务调度等场景。本版本为Go原版的Python重构实现，保持API兼容性。

---

## 目录结构

```
pyjobs/
├── app/
│   ├── api/
│   │   └── jobs.py          # 任务相关API接口
│   ├── core/
│   │   ├── scheduler.py     # 任务调度器（APScheduler）
│   │   └── runner.py        # 任务执行器（HTTP/命令/函数）
│   ├── models/
│   │   ├── base.py          # 数据库基础模型
│   │   ├── job.py           # 任务数据模型
│   │   ├── admin.py         # 管理员数据模型
│   │   └── log.py           # 日志数据模型
│   ├── function/
│   │   ├── common.py        # 通用解析函数
│   │   ├── registry.py      # 函数注册与热加载
│   │   └── user_funcs/      # 用户自定义函数目录
│   ├── middlewares/
│   │   └── ip_control.py    # IP控制中间件
│   ├── config.py            # 配置管理
│   ├── deps.py              # 数据库依赖注入
│   └── main.py              # FastAPI应用入口
├── scripts/
│   └── pyjobs.service       # systemd服务文件
├── cli.py                   # 命令行接口
├── Makefile                 # 构建和部署工具
├── requirements.txt         # Python依赖包
└── README.md               # 项目说明文档
```

---

## 业务流程概览

1. **任务管理**：增删改查任务 → 配置执行模式（HTTP/命令/函数） → 定时调度
2. **任务执行**：按cron表达式自动触发 → 记录执行日志 → 支持手动触发/停止/重启
3. **日志管理**：系统日志、任务日志分离，支持查询与下载
4. **IP控制**：支持白名单、黑名单，灵活配置
5. **系统监控**：健康检查、任务状态、API文档自带
6. **函数热加载**：支持运行时动态加载自定义函数

---

## 快速开始

### 环境要求
- **Python 3.8+** (最低要求)
- **Python 3.10+** (推荐)
- **Python 3.11+** (最佳性能)
- MySQL 5.7+/SQLite 3.x
- Windows/Linux/macOS

### Python版本说明
- **最低版本**: Python 3.8 (确保兼容性)
- **推荐版本**: Python 3.10 或 3.11 (稳定性和性能)
- **最佳版本**: Python 3.11+ (最新特性和性能优化)
- **测试版本**: Python 3.8.10, 3.9.13, 3.10.11, 3.11.5, 3.12.0

> 💡 **版本选择建议**:
> - 生产环境: Python 3.10 或 3.11
> - 开发环境: Python 3.11 或 3.12
> - 兼容性考虑: Python 3.8 (最低要求)

### 安装与运行

#### 环境检查（推荐）
在开始之前，建议先检查Python版本和环境：

```bash
# 方式一：使用检查脚本
python check_version.py

# 方式二：使用Makefile
make env-check

# 方式三：手动检查
python --version
pip --version
```

#### 方式一：使用CLI命令行（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/hgc357341051/TimerJobs.git
cd jobs/python/pyjobs

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置数据库
# 编辑 app/config.py 或设置环境变量

# 5. 启动服务
# 前台模式（开发调试）
python cli.py start

# 后台模式（生产环境）
python cli.py start -d

# 守护进程模式（高可用）
python cli.py start -d -f
```

#### 方式二：使用Makefile

```bash
# 1. 安装依赖
make install

# 2. 前台模式运行
make start

# 3. 后台模式运行
make start-bg

# 4. 守护进程模式运行
make start-daemon

# 5. 查看状态
make status

# 6. 停止服务
make stop          # 停止后台模式
make stop-all      # 停止守护进程模式
```

#### 方式三：直接使用uvicorn

```bash
# 开发模式（热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 配置说明
- 配置文件位于 `app/config.py`，支持环境变量覆盖
- 支持 MySQL/SQLite 数据库切换
- 支持热更新：修改配置后可通过API或重启服务生效

### 主要API入口
- Swagger文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/health
- 任务状态：http://127.0.0.1:8000/jobs/jobStatus

---

## 命令行接口（CLI）

### 基本命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `start` | 前台模式启动 | `python cli.py start` |
| `start -d` | 后台模式启动 | `python cli.py start -d` |
| `start -d -f` | 守护进程模式启动 | `python cli.py start -d -f` |
| `stop` | 停止后台模式 | `python cli.py stop` |
| `stop -f` | 停止守护进程模式 | `python cli.py stop -f` |
| `status` | 查看运行状态 | `python cli.py status` |
| `daemon` | 进入守护模式 | `python cli.py daemon` |
| `restart` | 重启服务 | `python cli.py restart` |
| `reload` | 重载配置 | `python cli.py reload` |

### 启动模式说明

#### 1. 前台模式 (`start`)
- 直接在当前终端运行
- 适合开发调试
- 按 Ctrl+C 停止

#### 2. 后台模式 (`start -d`)
- 在后台运行，不占用当前终端
- PID文件保存在 `runtime/job.pid`
- 适合生产环境单实例部署

#### 3. 守护进程模式 (`start -d -f`)
- 启动守护进程，自动监控和重启业务进程
- 守护进程PID保存在 `runtime/daemon.pid`
- 业务进程PID保存在 `runtime/job.pid`
- 适合高可用生产环境

### 进程管理

```bash
# 查看运行状态
python cli.py status

# 停止后台进程
python cli.py stop

# 停止所有相关进程（守护进程模式）
python cli.py stop -f

# 重启服务
python cli.py restart

# 重载配置（发送信号给运行中的进程）
python cli.py reload
```

---

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

---

## 系统服务管理（Linux）

### 安装为系统服务

```bash
# 1. 安装依赖
make install

# 2. 安装系统服务（需要root权限）
sudo make install-service

# 3. 启动服务
sudo systemctl start pyjobs

# 4. 设置开机自启
sudo systemctl enable pyjobs

# 5. 查看服务状态
sudo systemctl status pyjobs

# 6. 查看服务日志
sudo journalctl -u pyjobs -f
```

### 服务管理命令

```bash
# 启动服务
sudo systemctl start pyjobs

# 停止服务
sudo systemctl stop pyjobs

# 重启服务
sudo systemctl restart pyjobs

# 重载配置
sudo systemctl reload pyjobs

# 查看状态
sudo systemctl status pyjobs

# 查看日志
sudo journalctl -u pyjobs -f

# 禁用开机自启
sudo systemctl disable pyjobs
```

### 卸载系统服务

```bash
# 卸载系统服务（需要root权限）
sudo make uninstall-service
```

---

## 主要功能与接口

### 任务管理

#### 创建任务 API (`POST /jobs/add`)

系统支持三种执行模式：**HTTP请求**、**系统命令**、**内置函数**。每种模式都有不同的参数配置。

##### 通用参数

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| `name` | string | 是 | 任务名称，唯一标识 | `"数据备份任务"` |
| `desc` | string | 否 | 任务描述 | `"每日凌晨备份数据库"` |
| `cron_expr` | string | 是 | Cron表达式，定义执行时间 | `"0 2 * * *"` |
| `mode` | string | 是 | 执行模式：`http`/`command`/`func` | `"http"` |
| `command` | string | 是 | 执行内容（根据mode不同而不同） | 见下方详细说明 |
| `state` | int | 否 | 任务状态：0=等待，1=执行中，2=停止 | `0` |
| `allow_mode` | int | 否 | 执行模式：0=并行，1=串行，2=立即执行 | `0` |
| `max_run_count` | int | 否 | 最大执行次数，0=无限制 | `0` |

##### 1. HTTP 模式 (`mode: "http"`)

用于调用外部 HTTP API 接口。

**command 格式说明：**
```
【url】URL地址
【mode】请求方式
【headers】请求头1:值1|||请求头2:值2
【data】POST数据
【cookies】Cookie字符串
【proxy】代理地址
【times】执行次数
【result】自定义结果判断字符串
```

**详细示例：**

1. **简单GET请求**
```json
{
  "name": "健康检查",
  "desc": "检查服务健康状态",
  "cron_expr": "0 */2 * * * *",
  "mode": "http",
  "command": "【url】https://api.example.com/health\n【mode】GET"
}
```

2. **POST请求带JSON数据**
```json
{
  "name": "数据同步",
  "desc": "同步用户数据",
  "cron_expr": "0 0 2 * * *",
  "mode": "http",
  "command": "【url】https://api.example.com/sync\n【mode】POST\n【headers】Content-Type:application/json\n【data】{\"action\":\"sync\",\"timestamp\":\"2024-01-01\"}"
}
```

3. **使用代理的请求（支持HTTP/SOCKS）**
```json
{
  "name": "代理请求",
  "desc": "通过代理访问API",
  "cron_expr": "0 */5 * * * *",
  "mode": "http",
  "command": "【url】https://api.example.com/data\n【mode】GET\n【proxy】http://proxy.example.com:8080"
}
```

4. **带Cookie的请求**
```json
{
  "name": "会话请求",
  "desc": "保持会话的API调用",
  "cron_expr": "0 0 */1 * * *",
  "mode": "http",
  "command": "【url】https://api.example.com/user/profile\n【mode】GET\n【cookies】sessionid=abc123; userid=456"
}
```

**配置参数说明：**

| 参数 | 说明 | 示例 |
|------|------|------|
| `【url】` | 请求的URL地址（必填） | `【url】https://api.example.com/endpoint` |
| `【mode】` | 请求方式，默认GET | `【mode】POST` |
| `【headers】` | 请求头，多个用`|||`分隔 | `【headers】Content-Type:application/json|||Authorization:Bearer token` |
| `【data】` | POST请求的数据 | `【data】{"key":"value"}` |
| `【cookies】` | Cookie字符串 | `【cookies】sessionid=123; userid=456` |
| `【proxy】` | 代理服务器地址（支持HTTP/SOCKS） | `【proxy】http://proxy.example.com:8080` |
| `【times】` | 执行次数，0=无限制 | `【times】3` |
| `【result】` | 自定义成功判断字符串 | `【result】success` |

##### 2. 命令模式 (`mode: "command"`)

用于执行系统命令或脚本。

**command 格式说明：**
```
【command】要执行的命令
【workdir】工作目录
【env】环境变量1|||环境变量2
【timeout】超时时间(秒)
```

**详细示例：**

1. **简单命令**
```json
{
  "name": "磁盘清理",
  "desc": "清理临时文件",
  "cron_expr": "0 0 4 * * *",
  "mode": "command",
  "command": "【command】find /tmp -name '*.tmp' -mtime +7 -delete"
}
```

2. **带工作目录的命令**
```json
{
  "name": "备份脚本",
  "desc": "执行数据库备份脚本",
  "cron_expr": "0 0 2 * * *",
  "mode": "command",
  "command": "【command】./backup.sh\n【workdir】/opt/scripts"
}
```

3. **带环境变量的命令**
```json
{
  "name": "环境变量命令",
  "desc": "使用特定环境变量执行命令",
  "cron_expr": "0 0 6 * * *",
  "mode": "command",
  "command": "【command】echo $CUSTOM_VAR\n【env】CUSTOM_VAR=test_value|||DEBUG=true"
}
```

4. **带超时的命令**
```json
{
  "name": "超时命令",
  "desc": "设置超时时间的命令",
  "cron_expr": "0 */10 * * * *",
  "mode": "command",
  "command": "【command】long-running-script.sh\n【timeout】60"
}
```

5. **Windows系统命令**
```json
{
  "name": "Windows清理",
  "desc": "清理Windows临时文件",
  "cron_expr": "0 0 5 * * *",
  "mode": "command",
  "command": "【command】del /q /f %TEMP%\\*.tmp"
}
```

**配置参数说明：**

| 参数 | 说明 | 示例 |
|------|------|------|
| `【command】` | 要执行的命令（必填） | `【command】ls -la` |
| `【workdir】` | 工作目录 | `【workdir】/opt/scripts` |
| `【env】` | 环境变量，多个用`|||`分隔 | `【env】PATH=/usr/bin|||DEBUG=true` |
| `【timeout】` | 超时时间（秒），默认30秒 | `【timeout】60` |

##### 3. 函数模式 (`mode: "func"`)

使用系统内置函数或用户自定义函数，支持参数传递。

**command 格式说明：**
```
【name】函数名
【arg】参数1,参数2,参数3
```

**内置函数列表：**

| 函数名 | 功能 | 参数格式 | 示例 |
|--------|------|----------|------|
| `Dayin` | 打印任务信息 | `参数1,参数2,参数3` | `Dayin 1,hello,true` |
| `Test` | 测试函数 | `任意参数` | `Test test123` |
| `Hello` | 问候函数 | `姓名` | `Hello 张三` |
| `Time` | 时间函数 | `时间格式` | `Time 2006-01-02 15:04:05` |
| `Echo` | 回显函数 | `任意文本` | `Echo Hello World` |
| `Math` | 数学计算 | `操作符,数字1,数字2` | `Math +,10,5` |
| `File` | 文件操作 | `操作,文件路径` | `File read,/path/to/file` |
| `Database` | 数据库操作 | `操作,SQL语句` | `Database query,SELECT * FROM users` |
| `Email` | 邮件发送 | `收件人,主题,内容` | `Email user@example.com,测试,邮件内容` |
| `SMS` | 短信发送 | `手机号,内容` | `SMS 13800138000,测试短信` |
| `Webhook` | Webhook调用 | `URL,数据` | `Webhook https://webhook.site/xxx,{"data":"value"}` |
| `Backup` | 备份操作 | `源路径,目标路径` | `Backup /data,/backup` |
| `Cleanup` | 清理操作 | `路径,天数` | `Cleanup /tmp,7` |
| `Monitor` | 监控检查 | `检查项` | `Monitor disk` |
| `Report` | 报告生成 | `报告类型` | `Report daily` |

**详细示例：**

1. **基础函数调用**
```json
{
  "name": "时间显示",
  "desc": "显示当前时间",
  "cron_expr": "0 */5 * * * *",
  "mode": "func",
  "command": "【name】Time\n【arg】2006-01-02 15:04:05"
}
```

2. **数学计算**
```json
{
  "name": "数学计算",
  "desc": "执行数学运算",
  "cron_expr": "0 */30 * * * *",
  "mode": "func",
  "command": "【name】Math\n【arg】+,100,50"
}
```

3. **文件操作**
```json
{
  "name": "文件检查",
  "desc": "检查文件状态",
  "cron_expr": "0 0 */2 * * *",
  "mode": "func",
  "command": "【name】File\n【arg】read,/var/log/app.log"
}
```

4. **数据库操作**
```json
{
  "name": "数据统计",
  "desc": "统计用户数量",
  "cron_expr": "0 0 1 * * *",
  "mode": "func",
  "command": "【name】Database\n【arg】query,SELECT COUNT(*) FROM users"
}
```

5. **复杂参数函数**
```json
{
  "name": "Dayin测试",
  "desc": "测试Dayin函数",
  "cron_expr": "0 */15 * * * *",
  "mode": "func",
  "command": "【name】Dayin\n【arg】1,hello,true"
}
```

**配置参数说明：**

| 参数 | 说明 | 示例 |
|------|------|------|
| `【name】` | 函数名（必填） | `【name】Time` |
| `【arg】` | 函数参数，用逗号分隔 | `【arg】参数1,参数2,参数3` |

##### Cron表达式说明

| 字段 | 允许值 | 特殊字符 | 说明 |
|------|--------|----------|------|
| 秒 | 0-59 | `* / , -` | 秒数（0-59） |
| 分 | 0-59 | `* / , -` | 分钟（0-59） |
| 时 | 0-23 | `* / , -` | 小时（0-23） |
| 日 | 1-31 | `* / , - ?` | 日期（1-31） |
| 月 | 1-12 | `* / , -` | 月份（1-12） |
| 周 | 0-7 | `* / , - ?` | 星期（0或7=周日） |

**常用Cron表达式示例：**

| 表达式 | 说明 |
|--------|------|
| `* * * * * *` | 每秒执行 |
| `0 * * * * *` | 每分钟执行 |
| `0 0 * * * *` | 每小时执行 |
| `0 0 0 * * *` | 每天0点执行 |
| `0 0 2 * * *` | 每天2点执行 |
| `0 30 9 * * *` | 每天9点30分执行 |
| `0 0 0 * * 1` | 每周一0点执行 |
| `0 0 0 1 * *` | 每月1号0点执行 |

#### 其他任务管理接口

- `POST /jobs/edit` 编辑任务
- `POST /jobs/del` 删除任务
- `GET /jobs/list` 任务列表（分页）
- `GET /jobs/read` 查询任务详情
- `POST /jobs/run` 手动运行
- `POST /jobs/stop` 停止任务
- `POST /jobs/restart` 重启任务
- `POST /jobs/runAll` 批量运行
- `POST /jobs/stopAll` 批量停止
- `POST /jobs/logs` 查询任务日志

### 日志与系统
- `GET /jobs/zapLogs` 系统日志
- `GET /health` 健康检查
- `GET /jobs/jobStatus` 任务调度状态
- `GET /jobs/jobState` 任务状态
- `GET /jobs/scheduler` 调度器任务
- `POST /jobs/checkJob` 任务校准
- `GET /jobs/switchState` 日志开关
- `GET /jobs/dbinfo` 数据库信息
- `POST /jobs/reload-config` 配置热重载

### IP控制
- `GET /jobs/ip-control/status` 查询IP控制状态
- `POST /jobs/ip-control/whitelist/add` 增加白名单
- `POST /jobs/ip-control/whitelist/remove` 移除白名单
- `POST /jobs/ip-control/blacklist/add` 增加黑名单
- `POST /jobs/ip-control/blacklist/remove` 移除黑名单

### 函数管理
- `GET /jobs/functions` 获取可用函数列表
- `POST /jobs/functions/reload` 函数热加载

---

## 函数热加载机制

### 自定义函数开发
- 在 `app/function/user_funcs/` 目录下放置自定义 `.py` 文件
- 所有非下划线开头的函数会自动注册到系统中
- 支持运行时热加载（无需重启服务）
- 可通过API `POST /jobs/functions/reload` 触发热加载

### 函数开发规范
```python
# 示例：app/function/user_funcs/my_functions.py
def my_custom_function(param1, param2):
    """
    自定义函数示例
    Args:
        param1: 参数1
        param2: 参数2
    Returns:
        执行结果
    """
    result = f"处理参数: {param1}, {param2}"
    print(result)
    return result

def another_function():
    """无参数函数示例"""
    return "Hello from custom function"
```

### 使用自定义函数
```json
{
  "name": "自定义函数测试",
  "desc": "调用用户自定义函数",
  "cron_expr": "0 */10 * * * *",
  "mode": "func",
  "command": "【name】my_custom_function\n【arg】参数1,参数2"
}
```

---

## 业务开发规范

- **API层**：所有业务逻辑集中在 `app/api/`，每个模块独立。
- **模型层**：数据结构定义在 `app/models/`，与数据库表结构一一对应。
- **中间件**：统一放在 `app/middlewares/`，如IP控制、CORS、限流等。
- **核心服务**：调度器和执行器在 `app/core/`，包括任务调度、执行逻辑。
- **函数库**：公共函数和自定义函数在 `app/function/`。
- **配置管理**：统一在 `app/config.py`，支持环境变量覆盖。
- **日志**：系统日志与任务日志分离，自动写入数据库。
- **API文档**：基于FastAPI自动生成，访问 `/docs` 查看。

---

## 二次开发与扩展

1. **新增业务模块**：
   - 在 `app/api/` 下添加新的API文件
   - 在 `app/models/` 下添加对应的数据模型
   - 在 `main.py` 中注册新的路由

2. **自定义任务执行模式**：
   - 在 `app/core/runner.py` 中实现新的执行器
   - 在任务配置中选择对应的 `mode`

3. **中间件扩展**：
   - 在 `app/middlewares/` 新增中间件
   - 在 `main.py` 中注册中间件

4. **自定义函数开发**：
   - 在 `app/function/user_funcs/` 下添加函数文件
   - 使用热加载机制动态注册

5. **数据库迁移**：
   - 使用 Alembic 进行数据库版本管理
   - 修改模型后生成迁移文件

---

## 部署与运维

### Docker 部署
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app/ ./app/
COPY cli.py .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "cli.py", "start", "-d", "-f"]
```

### Docker Compose 部署
```yaml
version: '3.8'

services:
  pyjobs:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql://user:password@mysql:3306/pyjobs
      - IP_WHITELIST=192.168.1.0/24
    depends_on:
      - mysql
    volumes:
      - ./logs:/app/logs

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=pyjobs
      - MYSQL_USER=user
      - MYSQL_PASSWORD=password
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

### Systemd 服务
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
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 环境变量配置
```bash
# 数据库配置
DATABASE_URL=mysql://user:password@localhost:3306/pyjobs
# 或 SQLite
DATABASE_URL=sqlite:///./pyjobs.db

# IP控制
IP_WHITELIST=192.168.1.0/24,10.0.0.0/8
IP_BLACKLIST=192.168.1.100

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/var/log/pyjobs/app.log

# 服务配置
HOST=0.0.0.0
PORT=8000
```

---

## 常见问题与支持

### 常见问题

1. **数据库连接失败**
   - 检查数据库服务状态
   - 验证连接字符串格式
   - 确认数据库用户权限

2. **任务执行失败**
   - 检查cron表达式格式
   - 验证命令/URL可访问性
   - 查看任务执行日志

3. **函数热加载失败**
   - 检查函数文件语法
   - 确认函数名不以下划线开头
   - 查看系统日志

4. **IP控制不生效**
   - 检查IP地址格式
   - 确认CIDR格式正确
   - 验证环境变量设置

5. **进程管理问题**
   - 检查PID文件是否存在
   - 确认进程是否正在运行
   - 查看系统日志

### 日志查看
- 系统日志：通过API `GET /jobs/zapLogs` 查看
- 任务日志：通过API `POST /jobs/logs` 查询
- 文件日志：检查配置的日志文件路径
- 服务日志：`sudo journalctl -u pyjobs -f`

### 性能优化建议
- 生产环境使用MySQL数据库
- 配置合适的数据库连接池
- 定期清理历史日志数据
- 使用反向代理（如Nginx）进行负载均衡
- 使用守护进程模式确保高可用

---

## 与Go版本对比

| 特性 | Go版本 | Python版本 | 说明 |
|------|--------|------------|------|
| 执行模式 | HTTP/命令/函数 | HTTP/命令/函数 | 完全兼容 |
| 数据库 | MySQL/SQLite | MySQL/SQLite | 完全兼容 |
| API接口 | 完全兼容 | 完全兼容 | 保持一致性 |
| 函数热加载 | 支持 | 支持 | Python版本更灵活 |
| 代理支持 | HTTP | HTTP/SOCKS | Python版本更全面 |
| 部署方式 | 二进制/Docker | Python/Docker | 各有优势 |
| 开发效率 | 编译型 | 解释型 | Python开发更快 |
| 进程管理 | CLI命令 | CLI命令+Makefile | Python版本更丰富 |
| 系统服务 | systemd | systemd | 完全兼容 |

---

## 贡献与联系方式

- Fork 项目，提交 PR
- 作者：小胡
- QQ：357341051
- 邮箱：357341051@qq.com

---

## License

MIT 

## 测试相关

### 运行测试

```bash
# 安装测试依赖
pip install -r requirements-test.txt

# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_api.py -v
python -m pytest tests/test_models.py -v
python -m pytest tests/test_core.py -v

# 运行测试并生成覆盖率报告
python -m pytest tests/ --cov=app --cov-report=term-missing --cov-report=html

# 运行测试并生成HTML报告
python -m pytest tests/ --html=test_report.html --self-contained-html
```

### 使用测试脚本

```bash
# 查看帮助
python run_tests.py --help

# 运行所有测试
python run_tests.py --all

# 运行特定类型测试
python run_tests.py --api
python run_tests.py --models
python run_tests.py --core

# 运行测试并生成覆盖率报告
python run_tests.py --coverage

# 完整测试流程
python run_tests.py --full
```

### 使用Makefile

```bash
# 查看所有命令
make help

# 安装开发依赖
make install-dev

# 运行测试
make test
make test-unit
make test-api
make test-models
make test-core
make test-all
make test-coverage
make test-html

# 代码质量检查
make quality
make format

# 完整测试流程
make test-full
```

### 测试类型

- **单元测试**: 测试单个函数和类
- **API测试**: 测试HTTP接口
- **模型测试**: 测试数据模型
- **核心功能测试**: 测试任务执行和调度
- **中间件测试**: 测试IP控制等中间件
- **集成测试**: 测试完整流程

### 测试覆盖率

项目要求测试覆盖率不低于80%。运行覆盖率测试后，可以在`htmlcov/`目录查看详细的HTML报告。

## API使用

### 创建任务

```bash
curl -X POST "http://localhost:8000/jobs/add" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试任务",
    "desc": "这是一个测试任务",
    "cron_expr": "0 0 * * *",
    "mode": "http",
    "command": "https://httpbin.org/get",
    "allow_mode": 0,
    "max_run_count": 10
  }'
```

### 获取任务列表

```bash
curl -X GET "http://localhost:8000/jobs/list"
```

### 手动运行任务

```bash
curl -X POST "http://localhost:8000/jobs/run?id=1"
```

### 停止任务

```bash
curl -X POST "http://localhost:8000/jobs/stop?id=1"
```

## 配置说明

### 任务模式

- `http`: HTTP请求任务
- `command`: 系统命令任务
- `func`: Python函数任务

### 执行模式

- `0`: 并发执行（默认）
- `1`: 串行执行
- `2`: 立即执行

### Cron表达式

支持标准Cron表达式格式：`分 时 日 月 周`

示例：
- `0 0 * * *`: 每天0点执行
- `*/5 * * * *`: 每5分钟执行
- `0 12 * * 1`: 每周一12点执行

## 开发指南

### 项目结构

```
pyjobs/
├── app/                    # 应用主目录
│   ├── api/               # API路由
│   ├── core/              # 核心功能
│   ├── function/          # 函数注册
│   ├── global/            # 全局配置
│   ├── middlewares/       # 中间件
│   └── models/            # 数据模型
├── tests/                 # 测试目录
│   ├── test_api.py        # API测试
│   ├── test_models.py     # 模型测试
│   ├── test_core.py       # 核心功能测试
│   └── test_middlewares.py # 中间件测试
├── data/                  # 数据目录
├── logs/                  # 日志目录
├── requirements.txt       # 生产依赖
├── requirements-test.txt  # 测试依赖
├── pytest.ini           # pytest配置
├── run_tests.py         # 测试运行脚本
├── Makefile             # Makefile
└── README.md            # 项目文档
```

### 添加新功能

1. 在相应模块中添加功能代码
2. 编写对应的测试用例
3. 运行测试确保功能正常
4. 更新文档

### 代码规范

项目使用以下工具确保代码质量：

- **Black**: 代码格式化
- **isort**: 导入排序
- **flake8**: 代码风格检查
- **mypy**: 类型检查

运行代码质量检查：

```bash
make quality
make format
```

## 部署

### Docker部署

```bash
# 构建镜像
docker build -t pyjobs .

# 运行容器
docker run -p 8000:8000 pyjobs

# 或使用docker-compose
docker-compose up -d
```

### 系统服务

```bash
# 复制服务文件
sudo cp scripts/pyjobs.service /etc/systemd/system/

# 启用服务
sudo systemctl enable pyjobs
sudo systemctl start pyjobs

# 查看状态
sudo systemctl status pyjobs
```

## 监控和维护

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看系统日志
journalctl -u pyjobs -f
```

### 数据库备份

```bash
# 备份数据库
cp data/jobs.db data/jobs.db.backup.$(date +%Y%m%d_%H%M%S)

# 恢复数据库
cp data/jobs.db.backup.20240101_120000 data/jobs.db
```

### 性能监控

```bash
# 查看进程状态
ps aux | grep python

# 监控资源使用
htop
```

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 查看端口占用
   lsof -i :8000
   
   # 杀死进程
   kill -9 <PID>
   ```

2. **数据库锁定**
   ```bash
   # 删除锁定文件
   rm -f data/jobs.db-journal
   ```

3. **权限问题**
   ```bash
   # 修改文件权限
   chmod 755 main.py
   chmod -R 755 app/
   ```

### 调试模式

```bash
# 启用调试日志
export LOG_LEVEL=DEBUG
python main.py
```

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 编写代码和测试
4. 运行测试确保通过
5. 提交Pull Request

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交Issue
- 发送邮件
- 参与讨论

---

**注意**: 这是一个企业级项目，建议在生产环境中使用前进行充分的测试和配置。 