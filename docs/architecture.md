# 系统架构设计

## 1. 架构总览

```
FastAPI (API 层)
    │
    ├── Application Layer（用例编排 / 服务编排）
    │       ├── Services（面向 API 的业务编排）
    │       └── Use Cases（具体业务流程）
    │
    ├── Domain Layer（领域模型）
    │       ├── Entities / Value Objects
    │       └── Repository Interfaces
    │
    ├── Infrastructure Layer（基础设施）
    │       ├── Database (SQLAlchemy + PostgreSQL)
    │       ├── Vector Store (ChromaDB)
    │       └── AI Providers / Chains / Tools
    │
    └── Core Layer（配置 / 日志 / 常量 / 异常）
```

## 2. 模块说明

| 模块 | 说明 |
| --- | --- |
| `app/core` | 全局配置、日志、异常、启动初始化逻辑 |
| `app/api` | FastAPI 路由、依赖、请求/响应模型、中间件 |
| `app/application` | 业务编排层，包含服务和用例，用于协调领域与基础设施 |
| `app/domain` | 领域模型、实体、值对象、仓储接口定义 |
| `app/infrastructure` | PostgreSQL、ChromaDB、LLM Provider、工具链等具体实现 |
| `app/tasks` | 异步任务与调度逻辑 |

## 3. 核心能力映射

| 能力 | 模块 |
| --- | --- |
| 多模型接入 + 路由 | `app/infrastructure/ai/providers`, `app/application/services/model_router_service.py` |
| Agent Runtime | `app/application/services/agent_runtime.py` |
| RAG Pipeline | `app/application/services/rag_service.py`, `app/infrastructure/vector_store` |
| 文件上传 + 解析 | `app/application/services/file_service.py` |
| 工具注册中心 | `app/application/services/tool_registry.py` |
| 对话 Session 管理 | `app/application/services/session_service.py` + `app/domain/entities/session.py` |
| 异步任务 | `app/tasks/worker.py`, `app/application/use_cases/*` |
| 数据访问 | `app/infrastructure/database` + `app/domain/repositories` |

## 4. 数据流 (示例：AI 食物识别)

1. `POST /food/ai` → FastAPI 路由负责请求验证
2. API 调用 `FoodRecognitionService`
3. 服务根据输入（文本/图片）调用 `TextFoodUseCase` 或 `ImageFoodUseCase`
4. 用例调用多模型路由器、RAG 服务、Agent Runtime
5. 结果写入 PostgreSQL（餐食、食材、任务状态）并写入向量库
6. 返回结构化响应。

## 5. 扩展策略
- 所有 Provider、工具、仓储都以接口/抽象定义，便于未来接入更多模型/数据库
- 运行时支持串行/并行执行，具备取消 Token 机制
- RAG Pipeline 允许按 namespace 切分，支持多知识库
- Task 模块基于 asyncio，未来可挂接 Celery、Temporal 等调度系统

