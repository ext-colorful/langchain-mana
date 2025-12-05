# 🤖 企业级 AI 智能体平台

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-1.0-orange.svg)](https://python.langchain.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

一个功能完整、高度可扩展的**企业级 AI 智能体平台**，支持多模型、RAG 知识库、工具集成和流式输出。

---

## ⚡ 快速开始（3 步）

```bash
# 1. 配置 API Key
cp .env.example .env
# 编辑 .env，添加至少一个模型的 API Key（OpenAI/DeepSeek/Qwen）

# 2. 启动服务（Docker）
docker-compose up -d

# 3. 验证服务
curl http://localhost:8000/health
# 访问 API 文档: http://localhost:8000/docs
```

**就是这么简单！** 🎉

---

## ✨ 核心特性

### 🤖 多智能体运行时
- ✅ 异步任务执行
- ✅ 任务取消支持
- ✅ 流式输出
- ✅ 工具调用与 RAG 集成

### 🧠 多模型支持
- ✅ OpenAI (GPT-4, GPT-3.5)
- ✅ DeepSeek (deepseek-chat)
- ✅ Qwen (qwen-turbo, qwen-plus)
- ✅ Anthropic (Claude 3)
- ✅ 智能路由：成本/速度/质量优化

### 📚 RAG 知识库
- ✅ 文件解析（PDF、Word、Markdown、HTML、TXT）
- ✅ 向量化与检索（ChromaDB）
- ✅ 命名空间隔离
- ✅ 相似度搜索

### 🛠️ 工具系统
- ✅ 内置工具：Calculator、Weather
- ✅ 动态工具注册
- ✅ 权限控制
- ✅ 可扩展架构

### 🏢 企业级功能
- ✅ PostgreSQL 元数据存储
- ✅ JWT 认证
- ✅ 审计日志
- ✅ 健康检查与监控
- ✅ Docker 一键部署

---

## 📖 文档导航

- **📘 [完整功能文档](README_PLATFORM.md)** - 详细的功能说明和 API 示例
- **🚀 [快速启动指南](docs/QUICKSTART.md)** - 5 分钟快速上手
- **🏗️ [系统架构文档](docs/architecture/SYSTEM_ARCHITECTURE.md)** - 架构设计和模块说明
- **📦 [交付总结](docs/DELIVERY_SUMMARY.md)** - 完整的交付清单

---

## 🎯 API 快速体验

### 创建一个 Agent

```bash
curl -X POST "http://localhost:8000/api/v1/agents/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Agent",
    "model_provider": "openai",
    "model_name": "gpt-3.5-turbo",
    "tools": ["calculator"],
    "system_prompt": "You are a helpful AI assistant."
  }'
```

### 运行 Agent

```bash
curl -X POST "http://localhost:8000/api/v1/agents/1/run" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is 123 * 456?"
  }'
```

### 创建知识库并上传文件

```bash
# 创建知识库
curl -X POST "http://localhost:8000/api/v1/knowledge/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Knowledge Base",
    "chunk_size": 1000
  }'

# 上传文件
curl -X POST "http://localhost:8000/api/v1/knowledge/1/upload" \
  -F "file=@document.pdf"

# 查询
curl -X POST "http://localhost:8000/api/v1/knowledge/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is this document about?",
    "knowledge_base_ids": [1]
  }'
```

更多示例请查看 [README_PLATFORM.md](README_PLATFORM.md)

---

## 🧪 运行示例

```bash
# 安装依赖（本地开发）
cd backend
pip install -r requirements.txt

# 运行示例
cd ../examples
python agent_example.py
```

示例包含：
1. 基础 Agent（带计算器工具）
2. RAG Agent（带知识库检索）
3. 多工具 Agent（计算器 + 天气）

---

## 🏗️ 系统架构

```
API Gateway (FastAPI)
       │
       ├─► Agent Runtime ──► Tool Registry
       │                      │
       ├─► Model Router       │
       │   (OpenAI/DeepSeek/Qwen/Claude)
       │                      │
       └─► RAG Pipeline ──────┘
           (Parser → Chunker → Embedder → Retrieval)
                      │
        ┌─────────────┴─────────────┐
        │                           │
   PostgreSQL                   ChromaDB
   (Metadata)                   (Vectors)
```

详细架构请查看 [SYSTEM_ARCHITECTURE.md](docs/architecture/SYSTEM_ARCHITECTURE.md)

---

## 📦 技术栈

- **Web**: FastAPI + Uvicorn
- **Database**: PostgreSQL 15 + SQLAlchemy 2.0
- **Vector DB**: ChromaDB 0.4.22
- **AI**: LangChain 1.0 + LangChain-OpenAI
- **Auth**: python-jose (JWT) + passlib
- **Container**: Docker + Docker Compose

---

## 🔧 本地开发

```bash
# 启动数据库
docker-compose up -d postgres chroma

# 安装依赖
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 配置环境
cp ../.env.example ../.env
# 编辑 .env

# 启动服务
uvicorn main:app --reload --port 8000
```

---

## 🧪 测试

```bash
cd backend
pytest tests/ -v
```

---

## 🔌 扩展开发

### 添加自定义工具

```python
from app.tools.base import BaseTool, ToolMetadata

class MyTool(BaseTool):
    @property
    def metadata(self):
        return ToolMetadata(name="my_tool", ...)
    
    async def execute(self, **kwargs):
        return {"result": "..."}
```

### 添加新模型提供商

在 `backend/app/core/config.py` 中配置，在 `backend/app/models/router.py` 中实现适配器。

详细指南请查看 [README_PLATFORM.md](README_PLATFORM.md#扩展开发)

---

## 📊 项目结构

```
backend/
├── app/
│   ├── api/v1/          # API 路由
│   ├── agents/          # Agent Runtime
│   ├── models/          # Model Router
│   ├── rag/             # RAG Pipeline
│   ├── tools/           # Tool Registry
│   ├── storage/         # Database Models
│   └── core/            # Config & Security
├── tests/               # 测试
└── main.py              # 应用入口

docs/                    # 完整文档
examples/                # 示例代码
docker-compose.yml       # Docker 配置
```

---

## 🛠️ 常见问题

### Q: 如何配置多个模型？
A: 在 `.env` 中配置多个 API Key，系统会自动识别可用模型。

### Q: 如何启用流式输出？
A: 调用 `/agents/{id}/stream` 接口（WebSocket，开发中）。

### Q: 支持哪些文件格式？
A: 目前支持 PDF、Word、Markdown、HTML、TXT。可通过实现 `BaseParser` 扩展。

更多问题请查看 [QUICKSTART.md](docs/QUICKSTART.md#常见问题)

---

## 🗺️ Roadmap

- [ ] WebSocket 流式输出
- [ ] 前端 UI（React + Next.js）
- [ ] 多 Agent 协作
- [ ] Workflow 可视化编排
- [ ] 更多内置工具
- [ ] Kubernetes 部署

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 📧 支持

- 📖 [完整文档](README_PLATFORM.md)
- 🚀 [快速启动](docs/QUICKSTART.md)
- 🏗️ [架构设计](docs/architecture/SYSTEM_ARCHITECTURE.md)

---

**立即开始构建你的 AI 智能体！** 🚀

```bash
./scripts/setup.sh
```
