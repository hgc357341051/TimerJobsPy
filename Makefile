# 小胡定时任务系统（Python版）Makefile

# 变量定义
APP_NAME = pyjobs
VERSION = 1.0.0
PYTHON = python3
PIP = pip3
UVICORN = uvicorn

# 目录
APP_DIR = app
RUNTIME_DIR = runtime
BUILD_DIR = build
DIST_DIR = dist

# 默认目标
.PHONY: help install build clean test run start start-bg start-daemon stop stop-all status restart reload dev docker release

# 默认目标
help:
	@echo "小胡定时任务系统（Python版） - 构建工具"
	@echo ""
	@echo "可用命令:"
	@echo "  install         - 安装依赖"
	@echo "  build           - 构建项目"
	@echo "  clean           - 清理构建文件"
	@echo "  test            - 运行测试"
	@echo "  run             - 前台模式运行程序"
	@echo "  start           - 前台模式启动"
	@echo "  start-bg        - 后台模式启动"
	@echo "  start-daemon    - 守护模式启动"
	@echo "  stop            - 停止后台模式"
	@echo "  stop-all        - 停止守护模式(所有进程)"
	@echo "  status          - 查看运行状态"
	@echo "  restart         - 重启服务"
	@echo "  reload          - 重载配置"
	@echo "  dev             - 开发模式运行"
	@echo "  docker          - 构建Docker镜像"
	@echo "  release         - 创建发布包"
	@echo ""
	@echo "使用示例:"
	@echo "  make start        # 前台模式运行"
	@echo "  make start-bg     # 后台模式运行"
	@echo "  make start-daemon # 守护模式运行"
	@echo "  make stop         # 停止后台进程"
	@echo "  make stop-all     # 停止所有进程"
	@echo "  make status       # 查看状态"

# 检查Python版本
check-version:
	@echo "检查Python版本..."
	$(PYTHON) check_version.py

# 检查环境
check-env: check-version
	@echo "检查运行环境..."
	$(PYTHON) -c "import sys; print(f'Python版本: {sys.version}')"
	@echo "检查项目结构..."
	@test -d app && test -f cli.py && echo "✅ 项目结构正确" || echo "❌ 项目结构错误"

# 完整环境检查
env-check: check-env
	@echo "检查依赖包..."
	$(PIP) list | grep -E "(fastapi|uvicorn|sqlalchemy|apscheduler)" || echo "⚠️  部分依赖包未安装"
	@echo "环境检查完成"

# 安装依赖
install:
	@echo "安装Python依赖..."
	$(PIP) install -r requirements.txt
	@echo "依赖安装完成"

# 安装生产依赖（不包含开发工具）
install-prod:
	@echo "安装生产依赖..."
	$(PIP) install fastapi uvicorn sqlalchemy apscheduler requests pydantic python-dotenv
	@echo "生产依赖安装完成"

# 安装开发依赖
install-dev:
	@echo "安装开发依赖..."
	$(PIP) install -r requirements.txt
	$(PIP) install black flake8 mypy pytest pytest-asyncio bandit locust pdoc3
	@echo "开发依赖安装完成"

# 构建项目
build:
	@echo "构建 $(APP_NAME)..."
	@mkdir -p $(BUILD_DIR)
	@cp -r $(APP_DIR) $(BUILD_DIR)/
	@cp requirements.txt $(BUILD_DIR)/
	@cp cli.py $(BUILD_DIR)/
	@cp README.md $(BUILD_DIR)/
	@echo "构建完成: $(BUILD_DIR)/"

# 清理构建文件
clean:
	@echo "清理构建文件..."
	@rm -rf $(BUILD_DIR) $(DIST_DIR) $(RUNTIME_DIR)
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "清理完成"

# 运行测试
test:
	@echo "运行测试..."
	$(PYTHON) -m pytest tests/ -v

# 前台模式运行程序
run:
	@echo "前台模式运行程序..."
	$(PYTHON) cli.py start

# 前台模式启动
start:
	@echo "前台模式启动..."
	$(PYTHON) cli.py start

# 后台模式启动
start-bg:
	@echo "后台模式启动..."
	$(PYTHON) cli.py start -d

# 守护模式启动
start-daemon:
	@echo "守护模式启动..."
	$(PYTHON) cli.py start -d -f

# 停止后台模式
stop:
	@echo "停止后台模式..."
	$(PYTHON) cli.py stop

# 停止守护模式(所有进程)
stop-all:
	@echo "停止守护模式(所有进程)..."
	$(PYTHON) cli.py stop -f

# 查看运行状态
status:
	@echo "查看运行状态..."
	$(PYTHON) cli.py status

# 重启服务
restart:
	@echo "重启服务..."
	$(PYTHON) cli.py restart

# 重载配置
reload:
	@echo "重载配置..."
	$(PYTHON) cli.py reload

# 开发模式运行
dev:
	@echo "启动开发模式..."
	$(UVICORN) $(APP_DIR).main:app --reload --host 0.0.0.0 --port 8000

# 更新依赖
deps:
	@echo "更新依赖..."
	$(PIP) install --upgrade -r requirements.txt

# 代码格式化
fmt:
	@echo "代码格式化..."
	@if command -v black >/dev/null 2>&1; then \
		black $(APP_DIR)/; \
	else \
		echo "black 未安装，请运行: pip install black"; \
	fi

# 代码检查
lint:
	@echo "代码检查..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 $(APP_DIR)/; \
	else \
		echo "flake8 未安装，请运行: pip install flake8"; \
	fi

# 类型检查
type-check:
	@echo "类型检查..."
	@if command -v mypy >/dev/null 2>&1; then \
		mypy $(APP_DIR)/; \
	else \
		echo "mypy 未安装，请运行: pip install mypy"; \
	fi

# 构建Docker镜像
docker:
	@echo "构建Docker镜像..."
	docker build -t $(APP_NAME):$(VERSION) .
	docker tag $(APP_NAME):$(VERSION) $(APP_NAME):latest

# 创建发布包
release: build
	@echo "创建发布包..."
	@mkdir -p $(DIST_DIR)
	@cd $(BUILD_DIR) && tar -czf ../$(DIST_DIR)/$(APP_NAME)-$(VERSION).tar.gz .
	@echo "发布包创建完成: $(DIST_DIR)/$(APP_NAME)-$(VERSION).tar.gz"

# 安装为系统服务（Linux）
install-service:
	@echo "安装系统服务..."
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "需要root权限安装系统服务"; \
		exit 1; \
	fi
	@cp scripts/pyjobs.service /etc/systemd/system/
	@systemctl daemon-reload
	@systemctl enable pyjobs
	@echo "系统服务安装完成，使用 systemctl start/stop/status pyjobs 管理"

# 卸载系统服务（Linux）
uninstall-service:
	@echo "卸载系统服务..."
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "需要root权限卸载系统服务"; \
		exit 1; \
	fi
	@systemctl stop pyjobs 2>/dev/null || true
	@systemctl disable pyjobs 2>/dev/null || true
	@rm -f /etc/systemd/system/pyjobs.service
	@systemctl daemon-reload
	@echo "系统服务卸载完成"

# 创建虚拟环境
venv:
	@echo "创建虚拟环境..."
	$(PYTHON) -m venv venv
	@echo "虚拟环境创建完成，使用 source venv/bin/activate 激活"

# 激活虚拟环境并安装依赖
setup: venv
	@echo "激活虚拟环境并安装依赖..."
	@source venv/bin/activate && $(PIP) install -r requirements.txt
	@echo "环境设置完成"

# 数据库迁移
migrate:
	@echo "执行数据库迁移..."
	@if command -v alembic >/dev/null 2>&1; then \
		alembic upgrade head; \
	else \
		echo "alembic 未安装，请运行: pip install alembic"; \
	fi

# 生成迁移文件
migrate-create:
	@echo "生成迁移文件..."
	@if command -v alembic >/dev/null 2>&1; then \
		read -p "请输入迁移描述: " message; \
		alembic revision --autogenerate -m "$$message"; \
	else \
		echo "alembic 未安装，请运行: pip install alembic"; \
	fi

# 初始化数据库
init-db:
	@echo "初始化数据库..."
	$(PYTHON) -c "from app.models.base import Base; from app.deps import engine; Base.metadata.create_all(bind=engine); print('数据库初始化完成')"

# 备份数据库
backup-db:
	@echo "备份数据库..."
	@mkdir -p backups
	@if [ -f "pyjobs.db" ]; then \
		cp pyjobs.db backups/pyjobs_$$(date +%Y%m%d_%H%M%S).db; \
		echo "数据库备份完成"; \
	else \
		echo "未找到数据库文件"; \
	fi

# 查看日志
logs:
	@echo "查看系统日志..."
	@if [ -d "$(RUNTIME_DIR)" ]; then \
		tail -f $(RUNTIME_DIR)/*.log; \
	else \
		echo "未找到日志文件"; \
	fi

# 性能测试
benchmark:
	@echo "运行性能测试..."
	@if command -v locust >/dev/null 2>&1; then \
		locust -f tests/locustfile.py --host=http://localhost:8000; \
	else \
		echo "locust 未安装，请运行: pip install locust"; \
	fi

# 安全扫描
security-scan:
	@echo "运行安全扫描..."
	@if command -v bandit >/dev/null 2>&1; then \
		bandit -r $(APP_DIR)/; \
	else \
		echo "bandit 未安装，请运行: pip install bandit"; \
	fi

# 生成API文档
docs:
	@echo "生成API文档..."
	@if command -v pdoc3 >/dev/null 2>&1; then \
		pdoc3 --html --output-dir docs $(APP_DIR)/; \
		echo "API文档生成完成，查看 docs/ 目录"; \
	else \
		echo "pdoc3 未安装，请运行: pip install pdoc3"; \
	fi

# Python定时任务系统 Makefile

.PHONY: help install install-dev test test-unit test-api test-models test-core test-all test-coverage test-html quality format clean run

# 默认目标
help:
	@echo "可用的命令:"
	@echo "  install      - 安装生产依赖"
	@echo "  install-dev  - 安装开发依赖"
	@echo "  test         - 运行所有测试"
	@echo "  test-unit    - 运行单元测试"
	@echo "  test-api     - 运行API测试"
	@echo "  test-models  - 运行模型测试"
	@echo "  test-core    - 运行核心功能测试"
	@echo "  test-all     - 运行所有测试"
	@echo "  test-coverage- 运行测试并生成覆盖率报告"
	@echo "  test-html    - 运行测试并生成HTML报告"
	@echo "  quality      - 检查代码质量"
	@echo "  format       - 格式化代码"
	@echo "  clean        - 清理临时文件"
	@echo "  run          - 运行应用"

# 安装依赖
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-test.txt

# 测试相关
test: test-all

test-unit:
	python -m pytest tests/ -m unit -v

test-api:
	python -m pytest tests/test_api.py -v

test-models:
	python -m pytest tests/test_models.py -v

test-core:
	python -m pytest tests/test_core.py -v

test-all:
	python -m pytest tests/ -v

test-coverage:
	python -m pytest tests/ --cov=app --cov-report=term-missing --cov-report=html

test-html:
	python -m pytest tests/ --html=test_report.html --self-contained-html

test-fast:
	python -m pytest tests/ -m "not slow" -v

test-integration:
	python -m pytest tests/ -m integration -v

# 代码质量
quality:
	flake8 app/ tests/ --max-line-length=120
	black --check app/ tests/
	isort --check-only app/ tests/
	mypy app/ --ignore-missing-imports

format:
	black app/ tests/
	isort app/ tests/

# 清理
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -f test_report.html

# 运行应用
run:
	python main.py

# 开发服务器
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 完整测试流程
test-full: install-dev format quality test-all test-coverage

# 性能测试
perf-test:
	locust -f tests/locustfile.py --host=http://localhost:8000

# 类型检查
type-check:
	mypy app/ --ignore-missing-imports

# 安全检查
security-check:
	bandit -r app/ -f json -o security_report.json
	safety check

# 文档生成
docs:
	pydoc-markdown --render-toc --output-dir docs/ app/

# Docker相关
docker-build:
	docker build -t pyjobs .

docker-run:
	docker run -p 8000:8000 pyjobs

docker-test:
	docker run --rm pyjobs python -m pytest tests/ -v

# 数据库相关
db-migrate:
	alembic upgrade head

db-rollback:
	alembic downgrade -1

db-reset:
	rm -f data/jobs.db
	python -c "from app.models.base import Base; from app.global.db import engine; Base.metadata.create_all(engine)"

# 监控和日志
logs:
	tail -f logs/app.log

monitor:
	watch -n 1 "ps aux | grep python | grep -v grep"

# 备份和恢复
backup:
	cp data/jobs.db data/jobs.db.backup.$(shell date +%Y%m%d_%H%M%S)

restore:
	@echo "请指定备份文件: make restore BACKUP_FILE=data/jobs.db.backup.20240101_120000"
	@if [ -n "$(BACKUP_FILE)" ]; then cp $(BACKUP_FILE) data/jobs.db; fi 