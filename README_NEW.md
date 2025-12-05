# 企业级食物识别与营养分析系统

## 项目介绍

这是一个基于 LangChain、FastAPI 和 PostgreSQL 构建的企业级 AI 智能体平台。系统支持：

- **多模型适配**：OpenAI、智谱 AI、Mock Provider（可扩展）
- **食物识别**：文本描述、图像识别
- **营养分析**：基于 RAG 的智能营养分析
- **向量检索**：ChromaDB + 自定义 Embedding
- **餐食管理**：完整的餐食与食材数据管理
- **会话管理**：对话历史记录
- **异步任务**：后台任务调度

## 项目架构

```
app/
├── api/                         # API 层
│   ├── routers/                 # 路由定义
│   ├── schemas/                 # 请求/响应模型
│   ├── dependencies/            # 依赖注入
│   └── middlewares/             # 中间件
├── application/                 # 应用层
│   ├── services/                # 业务服务
│   └── use_cases/               # 用例编排
├── core/                        # 核心配置
│   ├── config.py                # 配置管理
│   ├── logging.py               # 日志系统
│   ├── exceptions.py            # 异常定义
│   └── constants.py             # 常量
├── domain/                      # 领域层
│   ├── entities/                # 领域实体
│   └── repositories/            # 仓储接口
├── infrastructure/              # 基础设施层
│   ├── database/                # 数据库（PostgreSQL）
│   ├── vector_store/            # 向量库（ChromaDB）
│   └── ai/                      # AI 服务
│       ├── providers/           # 模型提供者
│       └── chains/              # LangChain 业务链
└── tasks/                       # 异步任务
```

## 快速开始

### 1. 安装依赖

```bash
cd /home/engine/project
pip install -e .
```

### 2. 配置环境

```bash
cp .env.example .env
# 编辑 .env 文件，配置 API 密钥和数据库连接
```

### 3. 初始化数据库

确保 PostgreSQL 已运行，然后使用以下命令创建表结构：

```python
# 在 Python shell 中运行
from sqlalchemy import create_engine
from app.infrastructure.database.models import Base

engine = create_engine("postgresql://user:pass@localhost/food_system")
Base.metadata.create_all(engine)
```

### 4. 启动服务

```bash
python -m app.server
# 或使用 uvicorn
uvicorn app.server:app --host 0.0.0.0 --port 5513 --reload
```

### 5. 访问 API 文档

浏览器访问：http://localhost:5513/docs

## API 示例

### 文本食物识别

```bash
curl -X POST "http://localhost:5513/api/v1/food/ai" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "timestamp": 1696234567,
    "description": "今天中午吃了一碗牛肉面，还有两个鸡蛋"
  }'
```

### 图片食物识别

```bash
curl -X POST "http://localhost:5513/api/v1/food/ai" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "timestamp": 1696234567,
    "image_url": "https://example.com/food.jpg"
  }'
```

## 核心特性

### 1. 多模型路由

系统自动根据任务类型路由到合适的模型：
- 文本识别 → OpenAI GPT-4
- 图像识别 → 智谱 GLM-4V-Plus
- 如果没有配置真实模型，自动降级到 MockProvider

### 2. RAG 检索增强

营养分析使用 RAG 技术：
1. 将食材信息向量化存储到 ChromaDB
2. 查询时检索最相关的食材数据
3. 结合 LLM 分析生成精准的营养成分

### 3. 企业级数据库设计

- **异步 ORM**：SQLAlchemy 2.0 + asyncpg
- **连接池管理**：生产级连接池配置
- **多表关联**：餐食、食材、会话等完整数据模型

### 4. 灵活可控的架构

- **依赖倒置**：所有仓储、服务都基于接口
- **工厂模式**：动态创建 Provider 和 Embedding
- **策略模式**：不同的识别策略（文本/图像）
- **依赖注入**：FastAPI 原生依赖注入系统

## 扩展指南

### 添加新模型提供者

```python
# app/infrastructure/ai/providers/custom_provider.py
from app.infrastructure.ai.providers.base import BaseLLMProvider

class CustomProvider(BaseLLMProvider):
    name = "custom"
    
    async def ainvoke(self, messages, **kwargs):
        # 实现你的调用逻辑
        pass
```

然后在 `ModelRouterService` 中注册。

### 添加新工具

实现 LangChain 的 `@tool` 装饰器即可：

```python
from langchain_core.tools import tool

@tool
def custom_tool(query: str) -> str:
    """工具描述"""
    return "结果"
```

### 添加新端点

```python
# app/api/routers/custom_router.py
from fastapi import APIRouter

router = APIRouter(prefix="/custom", tags=["custom"])

@router.get("/endpoint")
async def custom_endpoint():
    return {"message": "Hello"}
```

然后在 `app/server.py` 中注册路由。

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | PostgreSQL 连接 URL | `postgresql+asyncpg://...` |
| `OPENAI_API_KEY` | OpenAI API 密钥 | - |
| `ZHIPU_API_KEY` | 智谱 AI API 密钥 | - |
| `DEFAULT_LLM_PROVIDER` | 默认模型提供者 | `openai` |
| `CHROMA_PERSIST_DIRECTORY` | ChromaDB 存储路径 | `./data/chroma` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

完整列表请查看 `.env.example`。

## 生产部署

### Docker 部署（推荐）

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .
RUN pip install -e .

CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "5513"]
```

### 性能优化

- 使用 Gunicorn + Uvicorn workers
- 启用数据库连接池
- 配置 Redis 缓存
- 使用 Nginx 反向代理

## 开发指南

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
ruff check app/
ruff format app/
```

## 贡献

欢迎提交 Issue 和 PR！

## 许可证

MIT
