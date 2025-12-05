# 🚀 快速启动指南

## 最快 5 分钟启动

### 1. 配置 API Key

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env，至少配置一个模型的 API Key
# 例如：OPENAI_API_KEY=sk-your-key-here
vim .env
```

### 2. 启动服务

```bash
# 一键启动所有服务
./scripts/setup.sh

# 或手动启动
docker-compose up -d
```

### 3. 验证

```bash
# 访问 API 文档
open http://localhost:8000/docs

# 或检查健康状态
curl http://localhost:8000/health
```

### 4. 运行示例

```bash
cd examples
python agent_example.py
```

---

## 详细步骤

### 方式一：Docker Compose（推荐）

```bash
# 1. 克隆项目
git clone <repository-url>
cd ai-agent-platform

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加 API keys

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f backend

# 5. 访问服务
# API 文档: http://localhost:8000/docs
# 健康检查: http://localhost:8000/health
```

### 方式二：本地开发

```bash
# 1. 启动数据库服务
docker-compose up -d postgres chroma

# 2. 安装 Python 依赖
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# 3. 配置环境变量
cp ../.env.example ../.env
# 编辑 .env

# 4. 启动后端
uvicorn main:app --reload --port 8000
```

---

## API 快速测试

### 使用 cURL

```bash
# 1. 创建 Agent
curl -X POST "http://localhost:8000/api/v1/agents/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Agent",
    "model_provider": "openai",
    "model_name": "gpt-3.5-turbo",
    "tools": ["calculator"]
  }'

# 2. 运行 Agent
curl -X POST "http://localhost:8000/api/v1/agents/1/run" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is 2+2?"
  }'
```

### 使用 Python

```python
import requests

# 创建 Agent
response = requests.post(
    "http://localhost:8000/api/v1/agents/create",
    json={
        "name": "My Agent",
        "model_provider": "openai",
        "model_name": "gpt-3.5-turbo",
        "tools": ["calculator"]
    }
)
agent_id = response.json()["id"]

# 运行 Agent
response = requests.post(
    f"http://localhost:8000/api/v1/agents/{agent_id}/run",
    json={"message": "Calculate 123 * 456"}
)
print(response.json())
```

---

## 常见问题

### Q: 启动失败，显示端口被占用
**A:** 修改 docker-compose.yml 中的端口映射，或停止占用端口的服务。

### Q: API Key 配置后仍然无法调用模型
**A:** 
1. 检查 .env 文件格式是否正确
2. 重启服务：`docker-compose restart backend`
3. 查看日志：`docker-compose logs backend`

### Q: ChromaDB 连接失败
**A:** 
1. 确认 ChromaDB 容器已启动：`docker-compose ps`
2. 检查配置：`CHROMA_HOST=chroma` 和 `CHROMA_PORT=8000`

### Q: 文件上传失败
**A:** 
1. 检查文件大小是否超过限制（默认 100MB）
2. 确保 `backend/data/uploads` 目录存在且有写权限

---

## 下一步

- 📖 阅读 [README_PLATFORM.md](../README_PLATFORM.md) 了解完整功能
- 🏗️ 查看 [SYSTEM_ARCHITECTURE.md](architecture/SYSTEM_ARCHITECTURE.md) 了解架构设计
- 🧪 运行 `examples/agent_example.py` 查看示例
- 🔧 开发自定义工具和解析器

---

**问题反馈**: 如遇到问题，请查看日志或提交 Issue。
