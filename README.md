# 小胡定时任务系统（Python重构版）

一个高可用、可扩展、支持多种执行模式的企业级定时任务管理系统，适用于自动化运维、定时数据处理、批量任务调度等场景。本版本为Go原版的Python重构实现，保持API兼容性。

---

## 项目特性

- 多种任务执行模式：HTTP请求、系统命令、Python函数
- 灵活调度：支持Cron表达式、间隔调度、手动触发
- 高可用：守护进程模式，自动重启
- IP控制：白名单/黑名单
- 函数热加载：运行时动态加载自定义函数
- 完整API：RESTful接口 + Swagger文档
- 多数据库支持：MySQL/SQLite
- 进程管理：CLI命令行 + Makefile
- Docker支持：一键容器化部署
- 系统服务：systemd集成
- 异步任务执行：非阻塞API响应
- 智能调度器：按需更新任务

---

## 最新优化

### 2025年最新版本优化亮点

1. **异步任务执行**
   - 手动运行任务API现在使用线程异步执行，不再阻塞HTTP响应
   - 批量运行所有任务API同样采用异步执行方式
   - 添加任务并直接执行API优化了异步执行和清理逻辑

2. **智能调度管理**
   - 更新任务时智能检测是否需要重新调度，避免不必要的调度器操作
   - 重启任务API新增可选参数，支持重置执行次数
   - 调度器操作增加线程安全保护，防止并发问题

3. **数据库连接优化**
   - 使用上下文管理器自动关闭数据库连接
   - 增强数据库会话错误处理和日志记录
   - 为SQLite添加外键支持
   - 提供非API环境使用的数据库上下文管理器

4. **日志系统改进**
   - 优化文件句柄管理，防止资源泄漏
   - 改进日志写入逻辑，减少磁盘IO
   - 增加析构函数确保资源释放
   - 智能fsync策略，仅在关键日志时同步到磁盘

5. **错误处理增强**
   - 全面改进异常捕获和处理
   - 详细的错误日志记录
   - 数据库操作失败时自动回滚

---

## 目录结构

```
jobsPy/
├── app/                  # 主应用目录
│   ├── api/              # 任务相关API接口
│   ├── core/             # 调度器、执行器等核心逻辑
│   ├── function/         # 通用函数、注册与热加载
│   ├── middlewares/      # 中间件（如IP控制、校验）
│   ├── models/           # 数据库模型
│   ├── config.py         # 配置管理
│   ├── deps.py           # 依赖注入
│   └── main.py           # FastAPI应用入口
├── scripts/              # 辅助脚本目录
│   ├── setup_venv.py     # 跨平台虚拟环境自动创建脚本
│   ├── setup_venv.bat    # Windows一键虚拟环境批处理
│   ├── setup_venv.sh     # Linux/macOS一键虚拟环境Shell脚本
│   ├── pyjobs.service    # systemd服务文件
│   └── README.md         # 脚本使用说明
├── cli.py                # 命令行接口
├── Makefile              # 构建和部署工具
├── requirements.txt      # 生产依赖包
├── requirements-test.txt # 测试依赖包
├── run_tests.py          # 测试运行脚本
├── data/                 # 数据目录
├── logs/                 # 日志目录
├── tests/                # 测试用例
└── README.md             # 项目说明文档
```

---

## 环境要求

- **Python 3.8+**（最低要求，推荐 3.10+）
- MySQL 5.7+/SQLite 3.x
- Windows/Linux/macOS

---

## 快速开始

### 一键创建虚拟环境与安装依赖

本项目推荐使用 scripts 目录下的自动化脚本，快速完成虚拟环境创建和依赖安装。

#### 1. setup_venv.py（跨平台自动化脚本）

**功能说明：**
- 自动检测 Python 版本
- 自动创建 venv 虚拟环境
- 自动升级 pip
- 自动安装 requirements.txt 依赖
- 自动检测 requirements-test.txt 并可选安装测试依赖
- 兼容 Windows、Linux、macOS

**使用方法：**

```bash
# 进入项目根目录
cd jobsPy

# 运行脚本（Windows/Linux/macOS 通用）
python scripts/setup_venv.py

# 可选参数
# --test   安装测试依赖 requirements-test.txt
python scripts/setup_venv.py --test
```

**常见问题与注意事项：**
- 若提示找不到 python 命令，请尝试 python3
- 若 requirements.txt 路径不对，请检查当前目录
- 脚本会自动提示虚拟环境激活方式

---

#### 2. setup_venv.bat（Windows专用一键批处理）

**功能说明：**
- 一键创建 venv 虚拟环境
- 自动升级 pip
- 自动安装 requirements.txt
- 自动激活虚拟环境（可选）

**使用方法：**

1. 双击 scripts/setup_venv.bat 即可自动完成环境搭建
2. 或在命令行中运行：
   ```bat
   scripts\setup_venv.bat
   ```

**注意事项：**
- 若遇到"窗口一闪而过"，请用命令行运行以查看详细报错
- 若已存在 venv 目录，脚本会提示是否覆盖
- 激活虚拟环境后，命令行前缀会出现 (venv)

---

#### 3. setup_venv.sh（Linux/macOS专用Shell脚本）

**功能说明：**
- 一键创建 venv 虚拟环境
- 自动升级 pip
- 自动安装 requirements.txt
- 自动激活虚拟环境（可选）

**使用方法：**

```bash
# 赋予执行权限
chmod +x scripts/setup_venv.sh

# 运行脚本
./scripts/setup_venv.sh
```

**注意事项：**
- 若提示权限不足，请用 chmod +x 赋权
- 若已存在 venv 目录，脚本会提示是否覆盖
- 激活虚拟环境后，命令行前缀会出现 (venv)

---

#### 4. 常见问题

- **虚拟环境删除失败**：请确保没有终端正在使用 venv，必要时手动删除 venv 目录
- **依赖安装失败**：请检查网络连接，或更换国内 pip 源
- **pip 版本过低**：脚本会自动升级 pip，如遇权限问题请用管理员/超级用户权限运行

---

## 配置说明

### 配置文件位置

- 主配置文件：`app/config.py`
- 支持通过环境变量覆盖配置项（如数据库连接、日志路径等）

### 主要配置项说明

| 配置项           | 说明                         | 示例                                      |
|------------------|------------------------------|-------------------------------------------|
| DATABASE_URL     | 数据库连接字符串              | `sqlite:///./data/jobs.db`<br>`mysql://user:pwd@localhost:3306/pyjobs` |
| LOG_LEVEL        | 日志级别                      | `INFO`、`DEBUG`、`WARNING`                |
| LOG_FILE         | 日志文件路径                  | `/var/log/pyjobs/app.log`                 |
| HOST             | 服务监听地址                  | `0.0.0.0`                                 |
| PORT             | 服务端口                      | `8000`                                    |
| IP_WHITELIST     | 允许访问的IP段（逗号分隔）    | `192.168.1.0/24,10.0.0.0/8`               |
| IP_BLACKLIST     | 禁止访问的IP                  | `192.168.1.100`                           |

**环境变量覆盖示例：**

```bash
export DATABASE_URL=sqlite:///./data/jobs.db
export LOG_LEVEL=DEBUG
export HOST=0.0.0.0
export PORT=8000
```

---

## 启动与运行方式

### 1. 使用 CLI 命令行（推荐）

```bash
# 前台模式（开发调试）
python cli.py start

# 后台模式
python cli.py start -d

# 守护进程模式（高可用）
python cli.py start -d -f

# 停止服务
python cli.py stop
python cli.py stop -f  # 停止守护进程

# 查看状态
python cli.py status

# 重启服务
python cli.py restart
```

---

### 2. 使用 Makefile（推荐自动化/一键操作）

```bash
# 安装依赖
make install

# 前台模式运行
make start

# 后台模式运行
make start-bg

# 守护进程模式运行
make start-daemon

# 停止服务
make stop
make stop-all

# 查看状态
make status

# 代码质量检查
make quality
make format

# 运行测试
make test
make test-all
```

---

### 3. 直接使用 uvicorn 启动（适合开发/调试）

```bash
# 开发模式（热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

### 4. 作为 systemd 服务运行（Linux 推荐生产环境）

1. 复制服务文件
   ```bash
   sudo cp scripts/pyjobs.service /etc/systemd/system/
   ```
2. 启用并启动服务
   ```bash
   sudo systemctl enable pyjobs
   sudo systemctl start pyjobs
   ```
3. 查看服务状态和日志
   ```bash
   sudo systemctl status pyjobs
   sudo journalctl -u pyjobs -f
   ```

---

### 5. Docker 部署

**构建镜像：**
```bash
docker build -t pyjobs .
```

**运行容器：**
```bash
docker run -p 8000:8000 pyjobs
```

**使用 docker-compose：**
```yaml
version: '3.8'
services:
  pyjobs:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./data/jobs.db
      - IP_WHITELIST=192.168.1.0/24
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
```
```bash
docker-compose up -d
```

---

## 主要API入口

- Swagger文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/health
- 任务状态：http://127.0.0.1:8000/jobs/jobStatus

---

## 任务模式与配置说明

### 任务模式
- `http`：HTTP请求任务，支持GET/POST等多种请求方式
- `command`：系统命令任务，支持Shell/批处理命令
- `func`：Python函数任务，支持内置和自定义函数

### 任务配置参数
| 参数名         | 类型    | 必填 | 说明                       | 示例                      |
|----------------|---------|------|----------------------------|---------------------------|
| name           | string  | 是   | 任务名称                   | "数据备份任务"           |
| desc           | string  | 否   | 任务描述                   | "每日凌晨备份数据库"     |
| cron_expr      | string  | 是   | Cron表达式                 | "0 2 * * *"              |
| mode           | string  | 是   | 执行模式：http/command/func| "http"                   |
| command        | string  | 是   | 执行内容                   | 见下方详细说明            |
| allow_mode     | int     | 否   | 执行模式：0并行/1串行/2立即| 0                         |
| max_run_count  | int     | 否   | 最大执行次数，0为无限制     | 0                         |

### Cron表达式说明
- 标准格式：`分 时 日 月 周`
- 示例：
  - `0 0 * * *`：每天0点执行
  - `*/5 * * * *`：每5分钟执行
  - `0 12 * * 1`：每周一12点执行

### command 字段详细说明

#### 1. HTTP模式
- 支持GET/POST/PUT/DELETE等请求
- 可配置headers、data、cookies、proxy等
- 示例：
  ```
  【url】https://api.example.com/health
  【mode】GET
  【headers】Content-Type:application/json
  【data】{"key":"value"}
  【proxy】http://proxy.example.com:8080
  ```

#### 2. command模式
- 执行系统命令或脚本
- 可配置工作目录、环境变量、超时时间
- 示例：
  ```
  【command】ls -la
  【workdir】/opt/scripts
  【env】DEBUG=true|||PATH=/usr/bin
  【timeout】60
  ```

#### 3. func模式
- 执行内置或自定义Python函数
- 示例：
  ```
  【name】my_custom_function
  【arg】参数1,参数2
  ```

---

## API使用示例

### 创建任务
```bash
curl -X POST "http://localhost:8000/jobs/add" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试任务",
    "desc": "这是一个测试任务",
    "cron_expr": "0 0 * * *",
    "mode": "http",
    "command": "https://httpbin.org/get"
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

### 查询任务日志
```bash
curl -X POST "http://localhost:8000/jobs/logs" -d '{"job_id":1}'
```

---

## 主要API接口字段详细表

### 任务相关接口字段
| 字段名         | 类型    | 必填 | 说明                       | 示例                      |
|----------------|---------|------|----------------------------|---------------------------|
| id             | int     | 否   | 任务ID（编辑/查询时用）    | 1                         |
| name           | string  | 是   | 任务名称                   | "数据备份任务"           |
| desc           | string  | 否   | 任务描述                   | "每日凌晨备份数据库"     |
| cron_expr      | string  | 是   | Cron表达式                 | "0 2 * * *"              |
| mode           | string  | 是   | 执行模式：http/command/func| "http"                   |
| command        | string  | 是   | 执行内容                   | 见前文详细说明            |
| allow_mode     | int     | 否   | 执行模式：0并行/1串行/2立即| 0                         |
| max_run_count  | int     | 否   | 最大执行次数，0为无限制     | 0                         |
| state          | int     | 否   | 任务状态：0等待/1执行中/2停止| 0                      |
| last_run_time  | string  | 否   | 上次执行时间（只读）        | "2024-01-01 00:00:00"    |
| next_run_time  | string  | 否   | 下次执行时间（只读）        | "2024-01-02 00:00:00"    |

### 日志相关接口字段
| 字段名         | 类型    | 说明                       |
|----------------|---------|----------------------------|
| id             | int     | 日志ID                     |
| job_id         | int     | 关联任务ID                 |
| start_time     | string  | 执行开始时间               |
| end_time       | string  | 执行结束时间               |
| status         | int     | 执行状态（0成功/1失败）    |
| output         | string  | 执行输出/日志内容          |

---

## 内置函数开发规范

- 所有自定义函数文件放在 `app/function/user_funcs/` 目录下，文件名建议用小写字母和下划线。
- 每个函数必须为非下划线开头的全局函数。
- 函数参数和返回值类型建议加注释说明。
- 支持热加载：无需重启服务，通过API或CLI命令即可重新加载。
- 示例：

```python
# 文件：app/function/user_funcs/myfuncs.py

def hello(name: str) -> str:
    """问候函数"""
    return f"Hello, {name}!"

def add(a: int, b: int) -> int:
    """加法函数"""
    return a + b
```

- 热加载方法：
  - 通过API：`POST /jobs/functions/reload`
  - 通过CLI：`python cli.py reload-funcs`

---

## 测试与质量保障

### 运行测试

```bash
# 安装测试依赖
pip install -r requirements-test.txt

# 运行所有测试
python run_tests.py --all

# 运行特定类型测试
python run_tests.py --api
python run_tests.py --models
python run_tests.py --core

# 代码质量检查
python run_tests.py --quality
```

### 使用 Makefile 运行测试

```bash
make test           # 运行全部测试
make test-all       # 运行全部测试
make test-coverage  # 生成覆盖率报告
make quality        # 代码风格检查
make format         # 自动格式化
```

### 代码规范

- **Black**：自动代码格式化
- **isort**：导入排序
- **flake8**：代码风格检查
- **mypy**：类型检查

> 建议开发前先运行 `make quality`，提交前运行 `make test`，保证代码质量。

---

## 开发规范

- **API 层**：所有业务逻辑集中在 `app/api/`，每个模块独立。
- **模型层**：数据结构定义在 `app/models/`，与数据库表结构一一对应。
- **中间件**：统一放在 `app/middlewares/`，如IP控制、CORS、限流等。
- **核心服务**：调度器和执行器在 `app/core/`，包括任务调度、执行逻辑。
- **函数库**：公共函数和自定义函数在 `app/function/`。
- **配置管理**：统一在 `app/config.py`，支持环境变量覆盖。
- **日志**：系统日志与任务日志分离，自动写入数据库。
- **API文档**：基于FastAPI自动生成，访问 `/docs` 查看。
- **代码风格**：建议使用 Black、isort、flake8、mypy 保持风格统一。

---

## 二次开发与扩展指南

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
   - 推荐使用 Alembic 进行数据库版本管理
   - 修改模型后生成迁移文件
   - 运行 `alembic upgrade head` 应用迁移

---

## 数据库迁移与管理

### Alembic 使用流程

1. 安装 Alembic：
   ```bash
   pip install alembic
   ```
2. 初始化迁移环境：
   ```bash
   alembic init migrations
   ```
3. 配置 `alembic.ini` 和 `env.py`，指向你的数据库和模型
4. 生成迁移脚本：
   ```bash
   alembic revision --autogenerate -m "描述信息"
   ```
5. 应用迁移：
   ```bash
   alembic upgrade head
   ```

### 常用数据库管理命令

- 备份数据库：
  ```bash
  cp data/jobs.db data/jobs.db.backup.$(date +%Y%m%d_%H%M%S)
  ```
- 恢复数据库：
  ```bash
  cp data/jobs.db.backup.20240101_120000 data/jobs.db
  ```

---

## 生产环境部署建议

1. **推荐使用MySQL数据库**，并配置合适的连接池参数。
2. **日志目录和数据目录**请放在独立磁盘或分区，避免磁盘满影响服务。
3. **使用 systemd 或 supervisor 守护进程**，保证服务自动重启。
4. **定期备份数据库和日志**，可用脚本或crontab自动化。
5. **使用Nginx等反向代理**，实现负载均衡和安全防护。
6. **关闭未使用的API端口**，限制管理接口访问来源。
7. **定期升级依赖和安全补丁**，保持系统安全。
8. **生产环境建议关闭Swagger文档**，防止敏感信息泄露。
9. **配置环境变量**，避免敏感信息硬编码在配置文件中。
10. **监控服务健康状态**，可用Prometheus、Grafana等工具。

---

## 常见问题与FAQ

### 1. 数据库连接失败
- 检查数据库服务状态
- 验证连接字符串格式
- 确认数据库用户权限

### 2. 任务执行失败
- 检查 cron 表达式格式
- 验证命令/URL 可访问性
- 查看任务执行日志

### 3. 函数热加载失败
- 检查函数文件语法
- 确认函数名不以下划线开头
- 查看系统日志

### 4. IP控制不生效
- 检查 IP 地址格式
- 确认 CIDR 格式正确
- 验证环境变量设置

### 5. 虚拟环境删除失败
- 确保没有终端正在使用 venv，必要时手动删除 venv 目录

### 6. 依赖安装失败
- 检查网络连接，或更换国内 pip 源

### 7. pip 版本过低
- 脚本会自动升级 pip，如遇权限问题请用管理员/超级用户权限运行

### 8. 端口被占用
- 查看端口占用：`lsof -i :8000` 或 `netstat -ano | findstr 8000`
- 杀死进程：`kill -9 <PID>` 或 `taskkill /PID <PID> /F`

### 9. 数据库锁定
- 删除锁定文件：`rm -f data/jobs.db-journal`

### 10. 权限问题
- 修改文件权限：`chmod 755 main.py`，`chmod -R 755 app/`

### 11. 日志无法写入
- 检查日志目录权限，确保有写入权限

### 12. 配置热更新不生效
- 检查配置文件路径和环境变量设置
- 尝试重启服务

---

## scripts 目录详细说明

本项目提供了三个脚本来帮助您快速创建和管理Python虚拟环境：

### 📁 脚本文件

1. **setup_venv.py** - Python脚本（跨平台，推荐）
2. **setup_venv.bat** - Windows批处理脚本
3. **setup_venv.sh** - Unix/Linux/macOS Shell脚本

### 🚀 使用方法

#### Windows用户

- 推荐直接双击 scripts\setup_venv.bat
- 或在命令行中运行：
  ```cmd
  cd scripts
  setup_venv.bat
  ```
- 也可用 Python 脚本：
  ```cmd
  python scripts\setup_venv.py
  python scripts\setup_venv.py --install-test --force
  ```

#### Unix/Linux/macOS用户

- 推荐使用Shell脚本：
  ```bash
  chmod +x scripts/setup_venv.sh
  ./scripts/setup_venv.sh
  ```
- 也可用 Python 脚本：
  ```bash
  python3 scripts/setup_venv.py
  python3 scripts/setup_venv.py --install-test --force
  ```

### ⚙️ setup_venv.py 参数说明

| 参数                  | 说明                       | 默认值                |
|-----------------------|----------------------------|-----------------------|
| --venv-name VENV_NAME | 虚拟环境名称               | venv                  |
| --python-version VER  | 指定Python版本             | 当前python            |
| --requirements FILE   | 依赖文件                   | requirements.txt      |
| --test-requirements FILE | 测试依赖文件            | requirements-test.txt |
| --install-test        | 同时安装测试依赖           | -                     |
| --force               | 强制重新创建虚拟环境        | -                     |

#### 使用示例

```bash
# 创建默认虚拟环境
python scripts/setup_venv.py

# 同时安装主依赖和测试依赖
python scripts/setup_venv.py --install-test

# 删除现有环境并重新创建
python scripts/setup_venv.py --force

# 创建名为 myenv 的虚拟环境
python scripts/setup_venv.py --venv-name myenv

# 指定Python版本
python scripts/setup_venv.py --python-version 3.8
```

### 🎯 激活/退出虚拟环境

#### Windows
```cmd
venv\Scripts\activate.bat
# 退出：deactivate
```

#### Unix/Linux/macOS
```bash
source venv/bin/activate
# 退出：deactivate
```

### 📦 依赖管理

- 查看已安装包：`pip list`
- 安装新包：`pip install package_name`
- 更新依赖文件：`pip freeze > requirements.txt`

### 🧪 运行测试

激活虚拟环境后可运行：
```bash
python -m pytest
python -m pytest tests/test_api.py
python -m pytest --cov=app tests/
```

### 🔍 常见问题

1. **Python版本过低**：确保安装Python 3.8或更高
2. **权限问题**：Windows请用管理员身份，Unix请用sudo或检查目录权限
3. **网络问题**：可用清华源 `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/`
4. **依赖安装失败**：检查 requirements.txt 格式，或逐个安装

### 手动创建虚拟环境（脚本失效时）

```bash
python -m venv venv
# Windows: venv\Scripts\activate.bat
# Unix: source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 贡献方式与联系方式

### 贡献指南

1. Fork 项目
2. 创建功能分支
3. 编写代码和测试
4. 运行测试确保通过
5. 提交 Pull Request

### 联系方式

- 作者：小胡
- QQ：357341051
- 邮箱：357341051@qq.com
- [GitHub Issues](https://github.com/hgc357341051/TimerJobs/issues)

---

## 版本历史与更新日志

### v1.0.0 (2024-01-01)
- 🎉 首次发布Python重构版本
- ✅ 完全兼容Go版本API接口
- ✅ 支持HTTP/命令/函数三种执行模式
- ✅ 实现函数热加载功能
- ✅ 支持MySQL/SQLite数据库
- ✅ 提供CLI命令行和Makefile工具
- ✅ 支持Docker容器化部署
- ✅ 集成systemd系统服务

### 兼容性说明
- **API兼容性**：与Go版本API完全兼容，可直接迁移
- **数据库兼容性**：支持Go版本数据库，无需数据迁移
- **配置兼容性**：大部分配置项可直接使用
- **功能兼容性**：所有核心功能保持一致

---

## 性能优化建议

### 数据库优化
1. **连接池配置**
   ```python
   # 在 app/config.py 中配置
   DATABASE_POOL_SIZE = 20
   DATABASE_MAX_OVERFLOW = 30
   DATABASE_POOL_TIMEOUT = 30
   DATABASE_POOL_RECYCLE = 3600
   ```

2. **索引优化**
   ```sql
   -- 为常用查询字段添加索引
   CREATE INDEX idx_jobs_state ON jobs(state);
   CREATE INDEX idx_jobs_next_run ON jobs(next_run_time);
   CREATE INDEX idx_logs_job_id ON job_logs(job_id);
   CREATE INDEX idx_logs_start_time ON job_logs(start_time);
   ```

3. **查询优化**
   - 使用分页查询避免大量数据加载
   - 定期清理历史日志数据
   - 使用数据库连接池

### 内存使用优化
1. **日志管理**
   ```python
   # 配置日志轮转
   LOG_ROTATION = "1 day"
   LOG_RETENTION = "30 days"
   LOG_COMPRESSION = True
   ```

2. **任务执行优化**
   - 设置合理的任务超时时间
   - 避免长时间运行的任务
   - 使用异步执行提高并发性能

### 并发处理优化
1. **执行器配置**
   ```python
   # 配置并发执行器
   MAX_CONCURRENT_JOBS = 10
   JOB_TIMEOUT = 300  # 5分钟
   ```

2. **调度器优化**
   - 使用线程池处理任务
   - 避免任务执行时间重叠
   - 合理设置cron表达式

---

## 安全加固指南

### 访问控制
1. **IP白名单配置**
   ```bash
   # 只允许特定IP段访问
   export IP_WHITELIST="192.168.1.0/24,10.0.0.0/8"
   ```

2. **API访问控制**
   ```python
   # 在 app/middlewares/ 中添加认证中间件
   from fastapi import HTTPException, Depends
   from fastapi.security import HTTPBearer
   
   security = HTTPBearer()
   
   async def verify_token(token: str = Depends(security)):
       # 实现token验证逻辑
       if not is_valid_token(token):
           raise HTTPException(status_code=401, detail="Invalid token")
   ```

3. **管理员权限控制**
   ```python
   # 在API中添加权限检查
   async def require_admin(user: User = Depends(get_current_user)):
       if not user.is_admin:
           raise HTTPException(status_code=403, detail="Admin required")
   ```

### 数据加密
1. **敏感配置加密**
   ```python
   # 使用环境变量存储敏感信息
   DATABASE_PASSWORD = os.getenv("DB_PASSWORD")
   API_SECRET_KEY = os.getenv("API_SECRET_KEY")
   ```

2. **日志脱敏**
   ```python
   # 在日志中隐藏敏感信息
   def mask_sensitive_data(data: str) -> str:
       # 实现数据脱敏逻辑
       return re.sub(r'password=([^&\s]+)', 'password=***', data)
   ```

### 网络安全
1. **HTTPS配置**
   ```python
   # 使用SSL证书
   uvicorn.run(app, ssl_keyfile="key.pem", ssl_certfile="cert.pem")
   ```

2. **CORS配置**
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],
       allow_credentials=True,
       allow_methods=["GET", "POST"],
       allow_headers=["*"],
   )
   ```

3. **请求限流**
   ```python
   # 添加限流中间件
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
   ```

---

## 监控与告警

### 健康检查
1. **内置健康检查接口**
   ```bash
   # 检查服务状态
   curl http://localhost:8000/health
   
   # 检查数据库连接
   curl http://localhost:8000/health/db
   
   # 检查调度器状态
   curl http://localhost:8000/health/scheduler
   ```

2. **自定义健康检查**
   ```python
   # 在 app/api/health.py 中添加自定义检查
   @router.get("/health/custom")
   async def custom_health_check():
       return {
           "status": "healthy",
           "timestamp": datetime.now(),
           "version": "1.0.0"
       }
   ```

### 性能监控
1. **Prometheus指标**
   ```python
   # 添加性能指标收集
   from prometheus_client import Counter, Histogram, Gauge
   
   job_execution_total = Counter('job_execution_total', 'Total job executions')
   job_execution_duration = Histogram('job_execution_duration', 'Job execution duration')
   active_jobs = Gauge('active_jobs', 'Number of active jobs')
   ```

2. **自定义监控指标**
   ```python
   # 监控关键指标
   failed_jobs = Counter('failed_jobs', 'Number of failed jobs')
   successful_jobs = Counter('successful_jobs', 'Number of successful jobs')
   queue_size = Gauge('queue_size', 'Number of jobs in queue')
   ```

### 告警配置
1. **邮件告警**
   ```python
   # 配置邮件告警
   import smtplib
   from email.mime.text import MIMEText
   
   def send_alert_email(subject: str, message: str):
       msg = MIMEText(message)
       msg['Subject'] = subject
       msg['From'] = "alert@example.com"
       msg['To'] = "admin@example.com"
       
       with smtplib.SMTP('smtp.example.com', 587) as server:
           server.starttls()
           server.login("user", "password")
           server.send_message(msg)
   ```

2. **Webhook告警**
   ```python
   # 配置Webhook告警
   import httpx
   
   async def send_webhook_alert(webhook_url: str, message: dict):
       async with httpx.AsyncClient() as client:
           await client.post(webhook_url, json=message)
   ```

3. **告警规则配置**
   ```yaml
   # alerting.yml
   rules:
     - alert: JobExecutionFailed
       expr: failed_jobs > 5
       for: 5m
       labels:
         severity: warning
       annotations:
         summary: "Job execution failed"
         description: "More than 5 jobs failed in 5 minutes"
   ```

---

## 备份与恢复策略

### 数据备份
1. **数据库备份脚本**
   ```bash
   #!/bin/bash
   # backup_db.sh
   
   BACKUP_DIR="/backup/database"
   DATE=$(date +%Y%m%d_%H%M%S)
   DB_FILE="data/jobs.db"
   
   # 创建备份目录
   mkdir -p $BACKUP_DIR
   
   # 备份SQLite数据库
   cp $DB_FILE $BACKUP_DIR/jobs_$DATE.db
   
   # 压缩备份文件
   gzip $BACKUP_DIR/jobs_$DATE.db
   
   # 删除7天前的备份
   find $BACKUP_DIR -name "*.db.gz" -mtime +7 -delete
   
   echo "Database backup completed: jobs_$DATE.db.gz"
   ```

2. **MySQL备份脚本**
   ```bash
   #!/bin/bash
   # backup_mysql.sh
   
   BACKUP_DIR="/backup/database"
   DATE=$(date +%Y%m%d_%H%M%S)
   DB_NAME="pyjobs"
   DB_USER="user"
   DB_PASS="password"
   
   mkdir -p $BACKUP_DIR
   
   # 备份MySQL数据库
   mysqldump -u$DB_USER -p$DB_PASS $DB_NAME > $BACKUP_DIR/pyjobs_$DATE.sql
   
   # 压缩备份文件
   gzip $BACKUP_DIR/pyjobs_$DATE.sql
   
   # 删除7天前的备份
   find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
   
   echo "MySQL backup completed: pyjobs_$DATE.sql.gz"
   ```

3. **配置文件备份**
   ```bash
   #!/bin/bash
   # backup_config.sh
   
   BACKUP_DIR="/backup/config"
   DATE=$(date +%Y%m%d_%H%M%S)
   
   mkdir -p $BACKUP_DIR
   
   # 备份配置文件
   tar -czf $BACKUP_DIR/config_$DATE.tar.gz \
       app/config.py \
       scripts/ \
       requirements.txt \
       requirements-test.txt
   
   # 删除30天前的备份
   find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
   
   echo "Config backup completed: config_$DATE.tar.gz"
   ```

### 自动备份
1. **Crontab配置**
   ```bash
   # 编辑crontab
   crontab -e
   
   # 每天凌晨2点备份数据库
   0 2 * * * /opt/pyjobs/scripts/backup_db.sh >> /var/log/pyjobs/backup.log 2>&1
   
   # 每周日凌晨3点备份配置文件
   0 3 * * 0 /opt/pyjobs/scripts/backup_config.sh >> /var/log/pyjobs/backup.log 2>&1
   ```

2. **备份监控**
   ```python
   # 检查备份状态
   def check_backup_status():
       backup_dir = "/backup/database"
       latest_backup = max(glob.glob(f"{backup_dir}/*.db.gz"), key=os.path.getctime)
       backup_time = datetime.fromtimestamp(os.path.getctime(latest_backup))
       
       if datetime.now() - backup_time > timedelta(days=1):
           send_alert_email("Backup Failed", "Database backup is older than 1 day")
   ```

### 数据恢复
1. **SQLite恢复**
   ```bash
   # 停止服务
   python cli.py stop
   
   # 恢复数据库
   cp /backup/database/jobs_20240101_120000.db.gz data/jobs.db.gz
   gunzip data/jobs.db.gz
   
   # 启动服务
   python cli.py start
   ```

2. **MySQL恢复**
   ```bash
   # 恢复MySQL数据库
   gunzip -c /backup/database/pyjobs_20240101_120000.sql.gz | mysql -uuser -ppassword pyjobs
   ```

3. **配置文件恢复**
   ```bash
   # 恢复配置文件
   tar -xzf /backup/config/config_20240101_120000.tar.gz -C /
   ```

---

## API错误码说明

### HTTP状态码
| 状态码 | 说明 | 常见原因 |
|--------|------|----------|
| 200 | 成功 | 请求正常处理，包括任务创建、查询、更新、删除等操作 |
| 401 | 未授权 | 缺少认证信息或认证失败 |
| 403 | 禁止访问 | IP不在白名单、权限不足 |
| 404 | 资源不存在 | 任务ID不存在、接口路径错误 |

### 业务错误码
| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 400 | 无法确定客户端IP | 检查网络连接 |
| 403 | IP地址不被允许 | 添加IP到白名单或从黑名单移除 |
| 404 | 业务错误（包括参数验证失败、任务不存在等） | 检查请求参数和业务逻辑 |
| 500 | 服务器内部错误 | 检查服务器日志 |

### 错误响应格式
```json
{
  "code": 404,
  "msg": "任务不存在",
  "data": null
}
```

### 错误处理建议
1. **客户端错误处理**
   ```python
   import requests
   
   try:
       response = requests.post("http://localhost:8000/jobs/add", json=data)
       response.raise_for_status()
   except requests.exceptions.HTTPError as e:
       if e.response.status_code == 401:
           print("认证失败，请检查认证信息")
       elif e.response.status_code == 403:
           print("访问被拒绝，请检查IP白名单或权限")
       elif e.response.status_code == 404:
           print("资源不存在，请检查任务ID或接口路径")
       else:
           print(f"请求失败: {e}")
   ```

2. **服务端错误处理**
   ```python
   from app.models.base import error_response
   
   @router.post("/jobs/add")
   async def add_job(job: JobCreate):
       try:
           # 业务逻辑
           pass
       except JobNameExistsError:
           # 业务错误通过200状态码返回，在响应体中包含错误信息
           return error_response(code=404, msg="任务名称已存在")
       except ValidationError as e:
           return error_response(code=404, msg=str(e))
   ```

---

## 常用运维脚本示例

### 系统监控脚本
```bash
#!/bin/bash
# monitor_system.sh

# 检查服务状态
check_service_status() {
    if ! pgrep -f "python.*cli.py" > /dev/null; then
        echo "ERROR: PyJobs service is not running"
        send_alert "PyJobs服务未运行"
        return 1
    fi
    echo "PyJobs service is running"
}

# 检查磁盘空间
check_disk_space() {
    DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $DISK_USAGE -gt 80 ]; then
        echo "WARNING: Disk usage is ${DISK_USAGE}%"
        send_alert "磁盘使用率过高: ${DISK_USAGE}%"
    fi
}

# 检查内存使用
check_memory_usage() {
    MEMORY_USAGE=$(free | awk 'NR==2{printf "%.2f", $3*100/$2}')
    if (( $(echo "$MEMORY_USAGE > 80" | bc -l) )); then
        echo "WARNING: Memory usage is ${MEMORY_USAGE}%"
        send_alert "内存使用率过高: ${MEMORY_USAGE}%"
    fi
}

# 检查数据库大小
check_database_size() {
    DB_SIZE=$(du -h data/jobs.db | cut -f1)
    echo "Database size: $DB_SIZE"
}

# 发送告警
send_alert() {
    MESSAGE="$1"
    # 实现告警逻辑（邮件、短信、webhook等）
    echo "ALERT: $MESSAGE"
}

# 主函数
main() {
    echo "=== PyJobs System Monitor ==="
    echo "Time: $(date)"
    
    check_service_status
    check_disk_space
    check_memory_usage
    check_database_size
    
    echo "=== Monitor Complete ==="
}

main
```

### 日志清理脚本
```bash
#!/bin/bash
# cleanup_logs.sh

LOG_DIR="logs"
RETENTION_DAYS=30

echo "开始清理日志文件..."

# 清理应用日志
find $LOG_DIR -name "*.log" -mtime +$RETENTION_DAYS -delete

# 清理备份日志
find $LOG_DIR -name "*.log.*" -mtime +$RETENTION_DAYS -delete

# 清理临时文件
find $LOG_DIR -name "*.tmp" -delete

echo "日志清理完成"
```

### 性能分析脚本
```bash
#!/bin/bash
# performance_analysis.sh

echo "=== PyJobs Performance Analysis ==="

# 分析任务执行情况
echo "任务执行统计:"
sqlite3 data/jobs.db "
SELECT 
    COUNT(*) as total_jobs,
    SUM(CASE WHEN status = 0 THEN 1 ELSE 0 END) as successful_jobs,
    SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) as failed_jobs,
    AVG((julianday(end_time) - julianday(start_time)) * 24 * 3600) as avg_execution_time
FROM job_logs 
WHERE start_time >= datetime('now', '-7 days');
"

# 分析最耗时的任务
echo "最耗时的任务 (Top 10):"
sqlite3 data/jobs.db "
SELECT 
    j.name,
    AVG((julianday(l.end_time) - julianday(l.start_time)) * 24 * 3600) as avg_time
FROM job_logs l
JOIN jobs j ON l.job_id = j.id
WHERE l.start_time >= datetime('now', '-7 days')
GROUP BY j.id
ORDER BY avg_time DESC
LIMIT 10;
"

# 分析失败率最高的任务
echo "失败率最高的任务 (Top 10):"
sqlite3 data/jobs.db "
SELECT 
    j.name,
    COUNT(*) as total_executions,
    SUM(CASE WHEN l.status = 1 THEN 1 ELSE 0 END) as failed_executions,
    ROUND(SUM(CASE WHEN l.status = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as failure_rate
FROM job_logs l
JOIN jobs j ON l.job_id = j.id
WHERE l.start_time >= datetime('now', '-7 days')
GROUP BY j.id
HAVING total_executions > 5
ORDER BY failure_rate DESC
LIMIT 10;
"
```

### 一键部署脚本
```bash
#!/bin/bash
# deploy.sh

set -e

echo "开始部署 PyJobs..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "错误: 需要Python $required_version或更高版本，当前版本: $python_version"
    exit 1
fi

# 创建虚拟环境
echo "创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 升级pip
echo "升级pip..."
pip install --upgrade pip

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 创建必要目录
echo "创建目录..."
mkdir -p data logs

# 初始化数据库
echo "初始化数据库..."
python -c "
from app.models.base import Base
from app.deps import engine
Base.metadata.create_all(bind=engine)
print('数据库初始化完成')
"

# 设置权限
echo "设置权限..."
chmod +x cli.py
chmod +x scripts/*.sh

# 创建systemd服务
if command -v systemctl &> /dev/null; then
    echo "创建systemd服务..."
    sudo cp scripts/pyjobs.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable pyjobs
    echo "systemd服务已创建并启用"
fi

echo "部署完成！"
echo "启动服务: python cli.py start"
echo "查看状态: python cli.py status"
```

### 故障排查脚本
```bash
#!/bin/bash
# troubleshoot.sh

echo "=== PyJobs 故障排查工具 ==="

# 检查系统信息
echo "系统信息:"
echo "OS: $(uname -a)"
echo "Python: $(python3 --version)"
echo "内存: $(free -h | grep Mem)"
echo "磁盘: $(df -h /)"

# 检查服务状态
echo "服务状态:"
if pgrep -f "python.*cli.py" > /dev/null; then
    echo "✓ PyJobs服务正在运行"
    ps aux | grep "python.*cli.py" | grep -v grep
else
    echo "✗ PyJobs服务未运行"
fi

# 检查端口占用
echo "端口占用:"
netstat -tlnp | grep :8000 || echo "端口8000未被占用"

# 检查数据库
echo "数据库状态:"
if [ -f "data/jobs.db" ]; then
    echo "✓ 数据库文件存在"
    echo "数据库大小: $(du -h data/jobs.db | cut -f1)"
    
    # 检查数据库连接
    if python3 -c "from app.deps import engine; print('数据库连接正常')" 2>/dev/null; then
        echo "✓ 数据库连接正常"
    else
        echo "✗ 数据库连接失败"
    fi
else
    echo "✗ 数据库文件不存在"
fi

# 检查日志文件
echo "日志文件:"
if [ -d "logs" ]; then
    echo "✓ 日志目录存在"
    ls -la logs/ | head -5
else
    echo "✗ 日志目录不存在"
fi

# 检查配置文件
echo "配置文件:"
if [ -f "app/config.py" ]; then
    echo "✓ 配置文件存在"
else
    echo "✗ 配置文件不存在"
fi

# 检查依赖
echo "依赖检查:"
if python3 -c "import fastapi, sqlalchemy, apscheduler" 2>/dev/null; then
    echo "✓ 核心依赖已安装"
else
    echo "✗ 核心依赖缺失"
fi

echo "=== 故障排查完成 ==="
```

### 数据迁移脚本
```bash
#!/bin/bash
# migrate_data.sh

echo "=== PyJobs 数据迁移工具 ==="

# 从Go版本迁移数据
migrate_from_go() {
    GO_DB_PATH="$1"
    PYTHON_DB_PATH="data/jobs.db"
    
    if [ ! -f "$GO_DB_PATH" ]; then
        echo "错误: Go版本数据库文件不存在: $GO_DB_PATH"
        exit 1
    fi
    
    echo "开始从Go版本迁移数据..."
    
    # 备份当前数据库
    if [ -f "$PYTHON_DB_PATH" ]; then
        cp "$PYTHON_DB_PATH" "${PYTHON_DB_PATH}.backup.$(date +%Y%m%d_%H%M%S)"
        echo "已备份当前数据库"
    fi
    
    # 复制数据库文件
    cp "$GO_DB_PATH" "$PYTHON_DB_PATH"
    echo "数据库文件已复制"
    
    # 验证数据完整性
    echo "验证数据完整性..."
    python3 -c "
import sqlite3
conn = sqlite3.connect('$PYTHON_DB_PATH')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM jobs')
job_count = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM job_logs')
log_count = cursor.fetchone()[0]
print(f'任务数量: {job_count}')
print(f'日志数量: {log_count}')
conn.close()
"
    
    echo "数据迁移完成！"
}

# 导出数据
export_data() {
    OUTPUT_FILE="$1"
    
    echo "导出数据到: $OUTPUT_FILE"
    
    python3 -c "
import json
import sqlite3
from datetime import datetime

conn = sqlite3.connect('data/jobs.db')
cursor = conn.cursor()

# 导出任务
cursor.execute('SELECT * FROM jobs')
jobs = cursor.fetchall()
job_columns = [description[0] for description in cursor.description]

# 导出日志
cursor.execute('SELECT * FROM job_logs')
logs = cursor.fetchall()
log_columns = [description[0] for description in cursor.description]

data = {
    'export_time': datetime.now().isoformat(),
    'jobs': [dict(zip(job_columns, job)) for job in jobs],
    'logs': [dict(zip(log_columns, log)) for log in logs]
}

with open('$OUTPUT_FILE', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'导出完成: {len(jobs)} 个任务, {len(logs)} 条日志')
conn.close()
"
}

# 导入数据
import_data() {
    INPUT_FILE="$1"
    
    if [ ! -f "$INPUT_FILE" ]; then
        echo "错误: 导入文件不存在: $INPUT_FILE"
        exit 1
    fi
    
    echo "从文件导入数据: $INPUT_FILE"
    
    python3 -c "
import json
import sqlite3
from datetime import datetime

with open('$INPUT_FILE', 'r', encoding='utf-8') as f:
    data = json.load(f)

conn = sqlite3.connect('data/jobs.db')
cursor = conn.cursor()

# 清空现有数据
cursor.execute('DELETE FROM job_logs')
cursor.execute('DELETE FROM jobs')

# 导入任务
for job in data['jobs']:
    cursor.execute('''
        INSERT INTO jobs (name, cron, mode, target, timeout, state, next_run_time, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        job['name'], job['cron'], job['mode'], job['target'],
        job['timeout'], job['state'], job['next_run_time'],
        job['created_at'], job['updated_at']
    ))

# 导入日志
for log in data['logs']:
    cursor.execute('''
        INSERT INTO job_logs (job_id, start_time, end_time, status, result, error)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        log['job_id'], log['start_time'], log['end_time'],
        log['status'], log['result'], log['error']
    ))

conn.commit()
print(f'导入完成: {len(data[\"jobs\"])} 个任务, {len(data[\"logs\"])} 条日志')
conn.close()
"
}

# 主函数
case "$1" in
    "migrate")
        migrate_from_go "$2"
        ;;
    "export")
        export_data "$2"
        ;;
    "import")
        import_data "$2"
        ;;
    *)
        echo "用法: $0 {migrate|export|import} [文件路径]"
        echo "  migrate <go_db_path>  - 从Go版本迁移数据"
        echo "  export <output_file>  - 导出数据到JSON文件"
        echo "  import <input_file>   - 从JSON文件导入数据"
        exit 1
        ;;
esac
```

---

## 与Go版本对比表

| 特性 | Go版本 | Python版本 | 详细说明 |
|------|--------|------------|----------|
| **执行模式** | HTTP/命令/函数 | HTTP/命令/函数 | 完全兼容，Python版本支持更丰富的HTTP选项 |
| **数据库支持** | MySQL/SQLite | MySQL/SQLite | 完全兼容，支持相同的数据结构 |
| **API接口** | RESTful API | RESTful API | 100%兼容，可直接迁移 |
| **函数热加载** | 支持 | 支持 | Python版本更灵活，支持运行时动态加载 |
| **代理支持** | HTTP代理 | HTTP/SOCKS代理 | Python版本支持更多代理类型 |
| **部署方式** | 二进制/Docker | Python/Docker | Go版本部署更简单，Python版本开发更灵活 |
| **开发效率** | 编译型 | 解释型 | Python版本开发调试更快 |
| **进程管理** | CLI命令 | CLI命令+Makefile | Python版本提供更多管理工具 |
| **系统服务** | systemd | systemd | 完全兼容 |
| **性能表现** | 高并发 | 中等并发 | Go版本性能更好，Python版本功能更丰富 |
| **内存占用** | 低 | 中等 | Go版本内存占用更少 |
| **启动速度** | 快 | 中等 | Go版本启动更快 |
| **学习曲线** | 陡峭 | 平缓 | Python版本更容易上手 |
| **生态系统** | 丰富 | 非常丰富 | Python版本有更多第三方库支持 |
| **调试能力** | 有限 | 强大 | Python版本调试工具更丰富 |
| **热更新** | 不支持 | 支持 | Python版本支持配置和函数热更新 |

### 迁移建议
1. **新项目**：推荐使用Python版本，开发效率更高
2. **现有Go项目**：可逐步迁移，API完全兼容
3. **性能要求高**：考虑Go版本
4. **功能要求多**：推荐Python版本
5. **团队熟悉度**：根据团队技术栈选择

### 性能对比测试
```bash
# 性能测试脚本
#!/bin/bash
# benchmark.sh

echo "=== PyJobs 性能对比测试 ==="

# 测试任务创建性能
echo "测试任务创建性能..."
time python3 -c "
import requests
import time

start_time = time.time()
for i in range(100):
    response = requests.post('http://localhost:8000/jobs/add', json={
        'name': f'test_job_{i}',
        'cron': '*/5 * * * *',
        'mode': 'http',
        'target': 'http://example.com',
        'timeout': 30
    })
    if response.status_code != 201:
        print(f'创建任务失败: {response.text}')

end_time = time.time()
print(f'创建100个任务耗时: {end_time - start_time:.2f}秒')
"

# 测试任务查询性能
echo "测试任务查询性能..."
time python3 -c "
import requests
import time

start_time = time.time()
for i in range(1000):
    response = requests.get('http://localhost:8000/jobs/list')
    if response.status_code != 200:
        print(f'查询任务失败: {response.text}')

end_time = time.time()
print(f'查询1000次耗时: {end_time - start_time:.2f}秒')
"

# 测试并发性能
echo "测试并发性能..."
python3 -c "
import asyncio
import aiohttp
import time

async def test_concurrent():
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        tasks = []
        for i in range(50):
            task = session.get('http://localhost:8000/jobs/list')
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        success_count = sum(1 for r in responses if r.status == 200)
        print(f'并发50个请求，成功: {success_count}，耗时: {end_time - start_time:.2f}秒')

asyncio.run(test_concurrent())
"

echo "=== 性能测试完成 ==="
```

---

## License

MIT

---

如需更详细的API文档、二次开发支持或生产环境运维建议，欢迎随时联系作者！ 