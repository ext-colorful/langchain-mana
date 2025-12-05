# 项目打包指南

本项目使用 `pyproject.toml` 配置，支持多种打包方式。

## 方法一：使用 pip 构建（推荐）

### 1. 安装构建工具

```bash
# 确保已安装 build 工具
pip install build wheel
```

### 2. 构建分发包

```bash
# 在项目根目录执行
python -m build

# 或者使用 pip
pip install build
python -m build
```

构建完成后，会在 `dist/` 目录下生成：
- `agent-0.0.1.tar.gz` - 源码分发包
- `agent-0.0.1-py3-none-any.whl` - wheel 分发包（推荐）

### 3. 安装构建的包

```bash
# 安装 wheel 包（推荐，更快）
pip install dist/agent-0.0.1-py3-none-any.whl

# 或安装源码包
pip install dist/agent-0.0.1.tar.gz
```

## 方法二：使用 setuptools 直接构建

```bash
# 安装 setuptools 和 wheel
pip install setuptools wheel

# 构建
python setup.py sdist bdist_wheel

# 构建产物在 dist/ 目录
```

## 方法三：开发模式安装（开发时使用）

```bash
# 以可编辑模式安装，代码修改后立即生效
pip install -e .

# 安装开发依赖
pip install -e ".[dev]"
```

## 发布到 PyPI

### 1. 安装 twine（用于上传）

```bash
pip install twine
```

### 2. 检查构建产物

```bash
# 检查分发包
twine check dist/*
```

### 3. 上传到 PyPI

```bash
# 上传到测试 PyPI（推荐先测试）
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# 上传到正式 PyPI
twine upload dist/*
```

## 打包配置说明

项目配置在 `pyproject.toml` 中：

- **包名**: `agent`
- **版本**: `0.0.1`
- **构建后端**: `setuptools.build_meta`
- **包目录**: `src/agent` → 映射为 `agent` 包

## 常见问题

### 1. 打包时找不到包

确保 `src/agent/` 目录下有 `__init__.py` 文件。

### 2. 包含额外文件

如果需要包含非 Python 文件，在 `pyproject.toml` 中添加：

```toml
[tool.setuptools.package-data]
"*" = ["*.txt", "*.md", "*.json"]
```

### 3. 排除文件

创建 `.gitignore` 或 `MANIFEST.in` 文件来排除不需要的文件。

## 快速命令

```bash
# 一键构建
python -m build

# 清理构建产物
rm -rf dist/ build/ *.egg-info/

# 重新构建
rm -rf dist/ build/ *.egg-info/ && python -m build
```

