# 测试文档

本文档详细说明了Python定时任务系统的测试框架、测试类型、运行方式等。

## 测试框架概述

项目采用现代化的Python测试框架，包括：

- **pytest**: 主要测试框架
- **pytest-cov**: 测试覆盖率
- **pytest-asyncio**: 异步测试支持
- **pytest-mock**: Mock支持
- **pytest-html**: HTML报告生成
- **httpx**: HTTP客户端测试
- **mypy**: 类型检查
- **black**: 代码格式化
- **flake8**: 代码风格检查
- **isort**: 导入排序
- **locust**: 性能测试

## 测试目录结构

```
tests/
├── __init__.py              # 测试包初始化
├── test_api.py              # API接口测试
├── test_models.py           # 数据模型测试
├── test_core.py             # 核心功能测试
├── test_middlewares.py      # 中间件测试
└── locustfile.py            # 性能测试
```

## 测试类型

### 1. 单元测试 (Unit Tests)

测试单个函数、类或模块的功能。

**特点:**
- 快速执行
- 独立性强
- 易于调试
- 覆盖核心逻辑

**示例:**
```python
def test_parse_multiline_config_simple():
    """测试解析简单配置"""
    config_str = "https://httpbin.org/get"
    result = parse_multiline_config(config_str)
    assert result == {}
```

### 2. API测试 (API Tests)

测试HTTP接口的功能和响应。

**特点:**
- 测试完整请求-响应流程
- 验证状态码和响应内容
- 测试错误处理
- 模拟真实使用场景

**示例:**
```python
def test_create_job_success(self, client, valid_job_data):
    """测试成功创建任务"""
    response = client.post("/jobs/add", json=valid_job_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "任务创建成功" in data["msg"]
```

### 3. 模型测试 (Model Tests)

测试数据模型的定义、验证和关系。

**特点:**
- 测试数据库模型
- 验证字段约束
- 测试关联关系
- 测试CRUD操作

**示例:**
```python
def test_create_job(self, db_session):
    """测试创建任务"""
    job = Job(
        name="测试任务",
        cron_expr="0 0 * * *",
        command="https://httpbin.org/get"
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    
    assert job.id is not None
    assert job.name == "测试任务"
```

### 4. 核心功能测试 (Core Tests)

测试任务执行、调度等核心业务逻辑。

**特点:**
- 测试复杂业务逻辑
- 使用Mock模拟外部依赖
- 测试异常情况
- 验证执行结果

**示例:**
```python
@patch('requests.request')
def test_http_job_execution_success(self, mock_request, db_session):
    """测试HTTP任务执行成功"""
    # 模拟HTTP响应
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_request.return_value = mock_response
    
    # 执行测试
    run_job(job.id, force_run=True)
    
    # 验证结果
    mock_request.assert_called_once()
```

### 5. 中间件测试 (Middleware Tests)

测试IP控制、验证等中间件功能。

**特点:**
- 测试请求处理流程
- 验证中间件逻辑
- 测试安全控制
- 模拟不同请求场景

### 6. 集成测试 (Integration Tests)

测试多个组件协同工作的完整流程。

**特点:**
- 测试端到端流程
- 使用真实数据库
- 测试完整API调用链
- 验证系统整体功能

### 7. 性能测试 (Performance Tests)

使用Locust进行负载和压力测试。

**特点:**
- 测试并发性能
- 验证系统稳定性
- 发现性能瓶颈
- 提供性能基准

## 测试运行方式

### 1. 使用pytest直接运行

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_api.py -v

# 运行特定测试函数
pytest tests/test_api.py::TestJobAPI::test_create_job_success -v

# 运行标记的测试
pytest tests/ -m "unit" -v
pytest tests/ -m "not slow" -v

# 生成覆盖率报告
pytest tests/ --cov=app --cov-report=term-missing --cov-report=html

# 生成HTML报告
pytest tests/ --html=test_report.html --self-contained-html
```

### 2. 使用测试脚本

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

### 3. 使用Makefile

```bash
# 查看所有命令
make help

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

## 测试配置

### pytest.ini配置

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --color=yes
    --durations=10

markers =
    slow: 标记为慢速测试
    integration: 标记为集成测试
    unit: 标记为单元测试
    api: 标记为API测试
    models: 标记为模型测试
    core: 标记为核心功能测试
    middlewares: 标记为中间件测试

filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
    ignore::UserWarning

minversion = 6.0
timeout = 300

addopts = 
    --cov=app
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
    --cov-fail-under=80
```

### conftest.py配置

提供测试用的fixture和配置：

- 数据库会话管理
- 测试客户端
- 示例数据
- Mock对象

## 测试最佳实践

### 1. 测试命名

- 测试文件: `test_<module>.py`
- 测试类: `Test<ClassName>`
- 测试函数: `test_<function_name>_<scenario>`

### 2. 测试组织

- 按功能模块组织测试
- 使用描述性的测试名称
- 添加详细的文档字符串
- 使用适当的测试标记

### 3. 测试数据

- 使用fixture提供测试数据
- 避免硬编码测试数据
- 使用工厂模式创建测试对象
- 清理测试数据

### 4. Mock使用

- 模拟外部依赖
- 模拟网络请求
- 模拟文件系统操作
- 模拟时间相关操作

### 5. 断言

- 使用具体的断言
- 验证关键行为
- 检查边界条件
- 测试异常情况

### 6. 测试隔离

- 每个测试独立运行
- 清理测试状态
- 避免测试间依赖
- 使用事务回滚

## 覆盖率要求

项目要求测试覆盖率不低于80%，包括：

- 语句覆盖率 (Statement Coverage)
- 分支覆盖率 (Branch Coverage)
- 函数覆盖率 (Function Coverage)
- 行覆盖率 (Line Coverage)

### 查看覆盖率报告

```bash
# 生成HTML报告
pytest --cov=app --cov-report=html

# 查看报告
open htmlcov/index.html
```

## 性能测试

### 使用Locust

```bash
# 安装Locust
pip install locust

# 运行性能测试
locust -f tests/locustfile.py --host=http://localhost:8000

# 访问Web界面
# http://localhost:8089
```

### 性能测试场景

1. **正常负载测试**: 模拟正常用户行为
2. **压力测试**: 测试系统极限
3. **并发测试**: 测试并发处理能力
4. **稳定性测试**: 长时间运行测试

## 持续集成

### GitHub Actions配置

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      run: |
        pytest tests/ --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
```

## 故障排除

### 常见问题

1. **测试失败**
   - 检查测试环境
   - 验证依赖安装
   - 查看错误日志

2. **覆盖率不达标**
   - 添加缺失的测试用例
   - 检查测试覆盖的代码路径
   - 排除不需要测试的代码

3. **性能测试失败**
   - 检查目标服务状态
   - 调整测试参数
   - 分析性能瓶颈

### 调试技巧

1. **使用pdb调试**
   ```python
   import pdb; pdb.set_trace()
   ```

2. **使用pytest调试**
   ```bash
   pytest tests/ -s --pdb
   ```

3. **查看详细输出**
   ```bash
   pytest tests/ -v -s
   ```

## 测试维护

### 定期维护

1. **更新测试依赖**
2. **检查测试覆盖率**
3. **优化测试性能**
4. **更新测试文档**

### 测试审查

1. **代码审查包含测试**
2. **确保测试质量**
3. **验证测试有效性**
4. **保持测试同步**

---

通过完善的测试框架，我们确保系统的质量、稳定性和可维护性。建议在开发过程中持续运行测试，及时发现和修复问题。 