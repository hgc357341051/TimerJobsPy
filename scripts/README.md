# 虚拟环境自动生成脚本

本项目提供了三个脚本来帮助您快速创建Python虚拟环境：

## 📁 脚本文件

1. **`setup_venv.py`** - Python脚本（跨平台）
2. **`setup_venv.bat`** - Windows批处理脚本
3. **`setup_venv.sh`** - Unix/Linux/macOS Shell脚本

## 🚀 使用方法

### Windows用户

#### 方法1：使用批处理脚本（推荐）
```cmd
# 双击运行
scripts\setup_venv.bat

# 或在命令行中运行
cd scripts
setup_venv.bat
```

#### 方法2：使用Python脚本
```cmd
# 在项目根目录运行
python scripts\setup_venv.py

# 带参数运行
python scripts\setup_venv.py --install-test --force
```

### Unix/Linux/macOS用户

#### 方法1：使用Shell脚本
```bash
# 给脚本添加执行权限（首次使用）
chmod +x scripts/setup_venv.sh

# 运行脚本
./scripts/setup_venv.sh
```

#### 方法2：使用Python脚本
```bash
# 在项目根目录运行
python3 scripts/setup_venv.py

# 带参数运行
python3 scripts/setup_venv.py --install-test --force
```

## ⚙️ Python脚本参数

`setup_venv.py` 支持以下命令行参数：

```bash
python scripts/setup_venv.py [选项]

选项:
  --venv-name VENV_NAME        虚拟环境名称 (默认: venv)
  --python-version VERSION     指定Python版本 (例如: 3.8)
  --requirements FILE          依赖文件 (默认: requirements.txt)
  --test-requirements FILE     测试依赖文件 (默认: requirements-test.txt)
  --install-test               同时安装测试依赖
  --force                      强制重新创建虚拟环境
```

## 📋 使用示例

### 基本使用
```bash
# 创建默认虚拟环境
python scripts/setup_venv.py
```

### 安装测试依赖
```bash
# 同时安装主依赖和测试依赖
python scripts/setup_venv.py --install-test
```

### 强制重新创建
```bash
# 删除现有环境并重新创建
python scripts/setup_venv.py --force
```

### 自定义环境名称
```bash
# 创建名为 "myenv" 的虚拟环境
python scripts/setup_venv.py --venv-name myenv
```

### 指定Python版本
```bash
# 确保使用Python 3.8+
python scripts/setup_venv.py --python-version 3.8
```

## 🔧 脚本功能

所有脚本都会自动执行以下操作：

1. ✅ **检查Python版本** - 确保Python 3.8+
2. ✅ **创建虚拟环境** - 使用venv模块
3. ✅ **升级pip** - 确保使用最新版本
4. ✅ **安装主依赖** - 从requirements.txt安装
5. ✅ **安装测试依赖** - 可选，从requirements-test.txt安装
6. ✅ **显示激活说明** - 提供详细的使用指导

## 🎯 激活虚拟环境

### Windows
```cmd
# 激活虚拟环境
venv\Scripts\activate.bat

# 退出虚拟环境
deactivate
```

### Unix/Linux/macOS
```bash
# 激活虚拟环境
source venv/bin/activate

# 退出虚拟环境
deactivate
```

## 📦 依赖管理

### 查看已安装的包
```bash
pip list
```

### 安装新包
```bash
pip install package_name
```

### 更新依赖文件
```bash
pip freeze > requirements.txt
```

## 🧪 运行测试

激活虚拟环境后，可以运行测试：

```bash
# 运行所有测试
python -m pytest

# 运行特定测试文件
python -m pytest tests/test_api.py

# 生成测试覆盖率报告
python -m pytest --cov=app tests/
```

## 🔍 故障排除

### 常见问题

1. **Python版本过低**
   - 确保安装Python 3.8或更高版本
   - 使用 `python --version` 检查版本

2. **权限问题**
   - Windows: 以管理员身份运行
   - Unix: 使用 `sudo` 或检查目录权限

3. **网络问题**
   - 检查网络连接
   - 使用国内镜像源：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/`

4. **依赖安装失败**
   - 检查requirements.txt文件格式
   - 尝试逐个安装依赖包

### 手动创建虚拟环境

如果脚本无法工作，可以手动创建：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows: venv\Scripts\activate.bat
# Unix: source venv/bin/activate

# 升级pip
python -m pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-test.txt
```

## 📝 注意事项

- 虚拟环境文件夹（venv/）已添加到.gitignore中
- 建议在每次开发前激活虚拟环境
- 定期更新依赖包以获取安全补丁
- 在生产环境中使用requirements.txt的固定版本号 