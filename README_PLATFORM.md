# 🚀 企业级 AI 智能体平台

一个功能完整、高度可扩展的企业级 AI 智能体平台，支持多模型、RAG 知识库、工具集成和流式输出。

## ✨ 核心特性

### 1. **多智能体运行时（Agent Runtime）**
- ✅ 异步任务执行
- ✅ 任务取消（Cancellation Token）
- ✅ 流式输出
- ✅ 错误处理与重试
- ✅ 工具调用与 RAG 集成

### 2. **多模型支持与智能路由**
- ✅ OpenAI (GPT-4, GPT-3.5)
- ✅ DeepSeek (deepseek-chat, deepseek-coder)
- ✅ Qwen (qwen-turbo, qwen-plus, qwen-max)
- ✅ Anthropic (Claude 3 系列)
- ✅ 智能路由策略：成本优化、速度优化、质量优化

### 3. **RAG 知识库系统**
- ✅ 文件上传与解析（PDF、Word、Markdown、HTML、TXT）
- ✅ 智能文本切分（Chunking）
- ✅ 向量化与检索（基于 ChromaDB）
- ✅ 命名空间隔离
- ✅ 相似度检索与 Top-K

### 4. **工具注册中心（Tool Registry）**
- ✅ 内置工具：计算器、天气查询
- ✅ 动态工具注册
- ✅ 权限控制
- ✅ 可扩展架构

### 5. **企业级功能**
- ✅ PostgreSQL 元数据存储
- ✅ JWT 认证
- ✅ API 审计日志
- ✅ 健康检查
- ✅ 监控指标
- ✅ Docker 部署

---

## 📋 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Gateway                        │
│  [Authentication] [Rate Limit] [Audit] [Monitoring]        │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐ ┌────▼──────┐ ┌──────▼────────┐
│ Agent Runtime  │ │   Model   │ │ RAG Pipeline  │
│                │ │  Router   │ │               │
│ • Executor     │ │           │ │ • Parser      │
│ • Context      │ │ • OpenAI  │ │ • Chunking    │
│ • Streaming    │ │ • DeepSeek│ │ • Embedding   │
│ • Cancellation │ │ • Qwen    │ │ • Retrieval   │
└────────┬───────┘ │ • Claude  │ └───────┬───────┘
         │         └───────────┘         │
         │                               │
         │     ┌──────────────┐         │
         └────►│Tool Registry │◄────────┘
               │              │
               │ • Calculator │
               │ • Weather    │
               │ • Custom     │
               └──────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼────┐ ┌──────▼─────┐ ┌────▼─────┐
│ PostgreSQL │ │  ChromaDB  │ │  Storage │
│            │ │            │ │          │
│ • Users    │ │ • Vectors  │ │ • Files  │
│ • Agents   │ │ • Metadata │ │          │
│ • Sessions │ │            │ │          │
└────────────┘ └────────────┘ └──────────┘
```

详细架构文档：[docs/architecture/SYSTEM_ARCHITECTURE.md](docs/architecture/SYSTEM_ARCHITECTURE.md)

---

## 🚀 快速开始

### 前置要求
- Docker & Docker Compose
- Python 3.10+ (本地开发)
- PostgreSQL 15+
- 至少一个 LLM API Key

### 1. 克隆项目并配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API Keys
# 至少需要配置一个模型提供商的 API Key
vim .env
```

### 2. 使用 Docker Compose 启动

```bash
# 启动所有服务（PostgreSQL + ChromaDB + Backend）
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

### 3. 验证服务

```bash
# 健康检查
curl http://localhost:8000/health

# API 文档
open http://localhost:8000/docs
```

---

## 📖 API 使用示例

### 1. 创建 Agent

```bash
curl -X POST "http://localhost:8000/api/v1/agents/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "My First Agent",
    "description": "A helpful assistant with calculator tool",
    "model_provider": "openai",
    "model_name": "gpt-3.5-turbo",
    "temperature": 0.7,
    "system_prompt": "You are a helpful AI assistant.",
    "tools": ["calculator"],
    "rag_enabled": false
  }'
```

### 2. 运行 Agent

```bash
curl -X POST "http://localhost:8000/api/v1/agents/1/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "What is 123 * 456?"
  }'
```

### 3. 创建知识库

```bash
curl -X POST "http://localhost:8000/api/v1/knowledge/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "My Knowledge Base",
    "description": "Company documents",
    "chunk_size": 1000,
    "chunk_overlap": 200
  }'
```

### 4. 上传文件到知识库

```bash
curl -X POST "http://localhost:8000/api/v1/knowledge/1/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"
```

### 5. 查询知识库

```bash
curl -X POST "http://localhost:8000/api/v1/knowledge/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "query": "What are the company policies?",
    "knowledge_base_ids": [1],
    "top_k": 5
  }'
```

### 6. 列出可用模型

```bash
curl -X GET "http://localhost:8000/api/v1/models/list" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 7. 列出可用工具

```bash
curl -X GET "http://localhost:8000/api/v1/tools/list" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🧪 测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行所有测试
cd backend
pytest tests/ -v

# 运行特定测试
pytest tests/test_tools.py -v
pytest tests/test_agent_runtime.py -v
```

---

## 🔧 本地开发

### 安装依赖

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 启动开发服务器

```bash
# 确保 PostgreSQL 和 ChromaDB 已启动
docker-compose up -d postgres chroma

# 启动 FastAPI
uvicorn main:app --reload --port 8000
```

### 数据库迁移（Alembic）

```bash
# 初始化 Alembic
alembic init alembic

# 生成迁移
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

---

## 📦 项目结构

```
backend/
├── app/
│   ├── api/v1/              # API 路由
│   │   ├── agents.py        # Agent CRUD & 运行
│   │   ├── knowledge.py     # 知识库管理
│   │   ├── models.py        # 模型列表
│   │   └── tools.py         # 工具列表
│   ├── agents/              # Agent Runtime
│   │   └── runtime.py       # 执行引擎
│   ├── core/                # 核心配置
│   │   ├── config.py        # 配置管理
│   │   ├── database.py      # 数据库连接
│   │   └── security.py      # 认证与授权
│   ├── models/              # Model Router
│   │   └── router.py        # 模型路由器
│   ├── rag/                 # RAG Pipeline
│   │   ├── pipeline.py      # RAG 管道
│   │   └── parsers/         # 文件解析器
│   ├── storage/             # 存储层
│   │   ├── models.py        # SQLAlchemy 模型
│   │   └── chroma_db.py     # ChromaDB 管理
│   ├── tools/               # Tool Registry
│   │   ├── base.py          # 工具基类
│   │   └── builtin/         # 内置工具
│   ├── schemas/             # Pydantic Schemas
│   └── utils/               # 工具函数
├── tests/                   # 测试用例
├── main.py                  # 应用入口
├── requirements.txt         # Python 依赖
└── Dockerfile               # Docker 镜像

docs/
└── architecture/
    └── SYSTEM_ARCHITECTURE.md  # 系统架构文档

docker-compose.yml           # Docker Compose 配置
.env.example                 # 环境变量模板
```

---

## 🔌 扩展开发

### 添加自定义工具

```python
# backend/app/tools/builtin/my_tool.py
from ..base import BaseTool, ToolMetadata, ToolParameter
from typing import Any

class MyCustomTool(BaseTool):
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="my_tool",
            description="My custom tool description",
            parameters=[
                ToolParameter(
                    name="param1",
                    type="string",
                    description="Parameter description",
                    required=True
                )
            ],
            category="custom"
        )
    
    async def execute(self, param1: str) -> Any:
        # 实现你的工具逻辑
        return {"result": f"Processed: {param1}"}

# 在 app/tools/__init__.py 中注册
from .builtin.my_tool import MyCustomTool

def register_builtin_tools():
    tool_registry.register(CalculatorTool())
    tool_registry.register(WeatherTool())
    tool_registry.register(MyCustomTool())  # 添加你的工具
```

### 添加新的文件解析器

```python
# backend/app/rag/parsers/custom_parser.py
from .base import BaseParser
from langchain_core.documents import Document
from typing import List

class CustomParser(BaseParser):
    @property
    def supported_extensions(self) -> List[str]:
        return [".custom"]
    
    async def parse(self, file_path: str, metadata: dict = None) -> List[Document]:
        # 实现解析逻辑
        content = "Parsed content"
        return [Document(page_content=content, metadata=metadata or {})]
```

### 添加新的模型提供商

```python
# 在 backend/app/core/config.py 中添加配置
class ModelProviderConfig:
    PROVIDERS = {
        # ... 现有配置 ...
        "my_provider": {
            "api_key": settings.MY_PROVIDER_API_KEY,
            "base_url": settings.MY_PROVIDER_BASE_URL,
            "models": ["model-1", "model-2"],
            "default": "model-1"
        }
    }

# 在 backend/app/models/router.py 中实现适配器
def _create_model(self, provider: str, model_name: str, ...):
    # ... 现有代码 ...
    elif provider == "my_provider":
        from langchain_myprovider import ChatMyProvider
        return ChatMyProvider(...)
```

---

## 📊 监控与运维

### 健康检查

```bash
GET /health
```

返回：
```json
{
  "status": "healthy",
  "database": "ok",
  "chroma": "ok",
  "models": ["openai", "deepseek", "qwen"]
}
```

### 指标监控

```bash
GET /metrics
```

---

## 🛠️ 常见问题

### 1. ChromaDB 连接失败
**解决方案**：确保 ChromaDB 服务已启动，检查 `CHROMA_HOST` 和 `CHROMA_PORT` 配置。

### 2. 模型调用失败
**解决方案**：检查 API Key 是否正确配置，网络是否可访问模型提供商 API。

### 3. 文件上传后处理失败
**解决方案**：检查文件格式是否支持，查看后台日志获取详细错误信息。

### 4. 数据库连接错误
**解决方案**：确保 PostgreSQL 已启动，检查数据库配置和权限。

---

## 🗺️ 后续扩展建议

### 短期（1-2 周）
- [ ] 添加用户注册和登录接口
- [ ] 实现 WebSocket 流式输出
- [ ] 添加更多内置工具（搜索、邮件等）
- [ ] 完善单元测试覆盖率

### 中期（1-2 月）
- [ ] 前端 UI 开发（React + Next.js）
- [ ] Agent 配置可视化编辑器
- [ ] RAG 查询结果可视化
- [ ] 多租户支持
- [ ] 成本追踪与配额管理

### 长期（3-6 月）
- [ ] 多 Agent 协作框架
- [ ] Workflow 可视化编排
- [ ] 插件市场
- [ ] 企业级权限管理（RBAC）
- [ ] Kubernetes 部署支持
- [ ] 自动化测试与 CI/CD

---

## 📄 许可证

本项目采用 MIT 许可证。

---

## 🙏 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📧 联系方式

- 项目主页：https://github.com/your-org/ai-agent-platform
- 技术支持：support@your-domain.com
- 文档中心：https://docs.your-domain.com

---

**快速开始示例已包含在 `examples/` 目录中！** 🎉
