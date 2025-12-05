# 企业级 AI 智能体平台 - 系统架构文档

## 一、整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │ Agent Builder│  │  RAG Manager │  │  Chat Interface     │  │
│  └──────────────┘  └──────────────┘  └─────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/WebSocket
┌────────────────────────────┴────────────────────────────────────┐
│                       API Gateway (FastAPI)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │  Auth    │ │  Rate    │ │  Audit   │ │   Monitoring     │  │
│  │ Middleware│ │ Limiting │ │  Logger  │ │   Metrics        │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼─────────┐  ┌────────▼────────┐  ┌────────▼────────────┐
│  Agent Runtime  │  │  Model Router   │  │   RAG Pipeline      │
│                 │  │                 │  │                     │
│ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────────┐ │
│ │  Executor   │ │  │ │   OpenAI    │ │  │ │ File Parser     │ │
│ │  Context    │ │  │ │  DeepSeek   │ │  │ │ Chunking        │ │
│ │  Cancellation│ │  │ │   Qwen      │ │  │ │ Embedding       │ │
│ │  Streaming  │ │  │ │ Anthropic   │ │  │ │ Retrieval       │ │
│ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────────┘ │
└────────┬────────┘  └─────────────────┘  └──────────┬──────────┘
         │                                            │
         │           ┌──────────────────┐            │
         └──────────►│  Tool Registry   │◄───────────┘
                     │                  │
                     │ ┌──────────────┐ │
                     │ │ Weather Tool │ │
                     │ │ Calculator   │ │
                     │ │ Database     │ │
                     │ │ Custom Tools │ │
                     │ └──────────────┘ │
                     └──────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼─────────┐  ┌────────▼────────┐  ┌────────▼─────────────┐
│   PostgreSQL    │  │  ChromaDB       │  │   File Storage       │
│                 │  │                 │  │   (MinIO/Local)      │
│ • Users         │  │ • Vectors       │  │                      │
│ • Agents        │  │ • Embeddings    │  │ • Uploaded Files    │
│ • Sessions      │  │ • Metadata      │  │ • Parsed Content    │
│ • Messages      │  │ • Namespaces    │  │                      │
│ • Audit Logs    │  │                 │  │                      │
└─────────────────┘  └─────────────────┘  └──────────────────────┘
```

## 二、核心模块说明

### 1. API Gateway
**职责**：统一入口、鉴权、限流、审计
**技术**：FastAPI + Pydantic
**功能**：
- REST API：CRUD操作
- WebSocket：实时流式输出
- JWT认证
- API Key管理
- 请求审计日志

### 2. Agent Runtime
**职责**：智能体执行引擎
**技术**：asyncio + LangChain Runnable
**功能**：
- 异步任务执行
- 并行任务协调
- 任务取消（Cancellation Token）
- 消息流控制
- Step回调机制
- 错误恢复与重试

**核心类**：
```python
class AgentExecutor:
    async def run(self, input, config, callbacks)
    async def stream(self, input, config, callbacks)
    async def cancel(self, session_id)
```

### 3. Model Router
**职责**：多模型适配与动态路由
**技术**：LangChain ChatModel接口
**功能**：
- 统一LLM调用接口
- 基于策略的模型选择（成本/速度/质量）
- 自动重试与熔断
- 模型配额管理

**支持的模型**：
- OpenAI (GPT-4, GPT-3.5)
- DeepSeek (deepseek-chat)
- Qwen (qwen-turbo, qwen-plus)
- Anthropic (Claude)

**路由策略**：
```python
class RoutingStrategy(Enum):
    COST_OPTIMIZED = "cost"
    SPEED_OPTIMIZED = "speed"
    QUALITY_OPTIMIZED = "quality"
    FALLBACK = "fallback"
```

### 4. RAG Pipeline
**职责**：私有知识库构建与检索
**技术**：LangChain + ChromaDB
**流程**：

```
File Upload → Parser → Chunker → Embedder → Vector Store
                                                 ↓
User Query → Embedding → Retrieval → ReRank → Context
```

**支持的文件格式**：
- PDF (PyPDF2 / PDFPlumber)
- Word (python-docx)
- Excel (openpyxl)
- Markdown
- TXT
- HTML

**Chunking策略**：
- RecursiveCharacterTextSplitter
- Token-based splitting
- Semantic chunking (可选)

**Namespace隔离**：
- 按用户隔离
- 按知识库隔离
- 按文件隔离

### 5. Tool Registry
**职责**：工具注册与权限控制
**技术**：插件化架构
**功能**：
- 动态注册工具
- 权限控制（用户级、Agent级）
- 工具版本管理
- 参数验证

**内置工具**：
- Calculator（计算器）
- WebSearch（网络搜索，可选）
- WeatherAPI（天气查询）
- DatabaseQuery（数据库查询）

**工具接口**：
```python
class BaseTool(ABC):
    name: str
    description: str
    parameters: Dict
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        pass
```

### 6. Storage Layer

#### PostgreSQL（结构化数据）
**表结构**：
```sql
-- 用户表
users (id, username, email, api_key, created_at)

-- Agent配置表
agents (id, user_id, name, model_config, system_prompt, tools, created_at)

-- 会话表
sessions (id, agent_id, user_id, status, created_at, updated_at)

-- 消息表
messages (id, session_id, role, content, metadata, created_at)

-- 知识库表
knowledge_bases (id, user_id, name, namespace, created_at)

-- 文件表
files (id, kb_id, filename, file_type, status, created_at)

-- 审计日志表
audit_logs (id, user_id, action, resource, metadata, created_at)
```

#### ChromaDB（向量数据）
**Collection设计**：
- 每个知识库对应一个collection
- Metadata包含：file_id, chunk_index, user_id
- 支持按metadata过滤检索

### 7. Monitoring & Observability
**指标采集**：
- QPS / TPS
- 响应延迟（P50, P95, P99）
- 错误率
- 模型调用次数与成本
- 工具调用统计

**日志系统**：
- 结构化日志（JSON格式）
- 全链路追踪（Trace ID）
- 可回放的请求日志

**健康检查**：
```
GET /health
  - database: ok/error
  - chroma: ok/error
  - models: ok/error
```

## 三、数据流示例

### 场景1：用户创建Agent并对话

```
1. POST /api/v1/agents/create
   → 验证用户身份
   → 保存Agent配置到PostgreSQL
   → 返回agent_id

2. POST /api/v1/agents/{agent_id}/run
   → 加载Agent配置
   → Model Router选择模型
   → Agent Runtime执行
   → 调用Tool（如需要）
   → 查询RAG（如配置）
   → 返回结果
   → 记录审计日志

3. WebSocket /api/v1/agents/{agent_id}/stream
   → 建立连接
   → 接收用户消息
   → 流式返回Agent步骤：
     - event: agent_start
     - event: tool_call
     - event: rag_retrieve
     - event: model_response
     - event: agent_finish
```

### 场景2：上传文件并构建知识库

```
1. POST /api/v1/knowledge/upload
   → 保存文件到Storage
   → 创建File记录
   → 触发异步解析任务

2. Background Task
   → Parser解析文件
   → Chunker切分文本
   → Embedder生成向量
   → 存入ChromaDB
   → 更新File状态

3. POST /api/v1/agents/{agent_id}/run (with RAG)
   → 提取用户问题
   → Embedding查询向量
   → ChromaDB检索Top-K
   → 构造增强Prompt
   → 调用LLM生成回答
   → 返回结果 + 引用来源
```

## 四、扩展性设计

### 1. 模型扩展
- 新增模型只需实现`BaseModelAdapter`接口
- 在`ModelRegistry`中注册
- 无需修改核心逻辑

### 2. 工具扩展
- 新增工具继承`BaseTool`
- 注册到`ToolRegistry`
- Agent配置中引用

### 3. Parser扩展
- 实现`BaseParser`接口
- 注册到`ParserRegistry`
- 支持新文件格式

### 4. 存储扩展
- PostgreSQL可替换为MySQL
- ChromaDB可替换为Pinecone/Weaviate
- 通过适配器模式隔离

### 5. 前端扩展
- Agent Builder支持拖拽式配置
- 自定义工具UI
- Workflow可视化编辑器

## 五、安全与权限

### 1. 认证
- JWT Token
- API Key
- OAuth2（可选）

### 2. 授权
- RBAC（基于角色）
- 资源级权限控制
- Agent访问权限

### 3. 审计
- 所有API调用记录
- 敏感操作审计
- 数据访问追踪

### 4. 数据隔离
- 多租户隔离
- Namespace隔离
- 数据加密（可选）

## 六、部署架构

### 开发环境
```
docker-compose up
  - backend (FastAPI)
  - postgres
  - chroma
  - redis (可选)
```

### 生产环境
```
Kubernetes Deployment:
  - API Service (多副本)
  - Worker Service (异步任务)
  - PostgreSQL (StatefulSet)
  - ChromaDB (StatefulSet)
  - Nginx Ingress
  - Prometheus + Grafana
```

## 七、性能指标

### 目标SLA
- API响应时间：P95 < 500ms
- 流式首字延迟：< 1s
- 文件解析：1MB/s
- 向量检索：< 100ms
- 系统可用性：99.9%

### 优化策略
- 模型调用并行化
- 向量检索缓存
- 数据库连接池
- 异步任务队列
- CDN加速文件上传

---

**版本**: v1.0  
**最后更新**: 2024-12-05  
**作者**: AI Agent Platform Team
