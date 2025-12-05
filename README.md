# AI食物识别智能体

基于 LangGraph 实现的智能食物识别与营养分析系统，支持文本和图片两种输入方式识别食物，并自动分析营养成分。

## 功能特性

- 🍽️ **文本食物识别**：从文本描述中提取食物信息（菜品名称、描述、食材列表）
- 📷 **图片食物识别**：从图片中识别食物信息（使用智谱AI的GLM-4V-Plus模型）
- 🥗 **营养成分分析**：自动分析食物的详细营养成分（卡路里、蛋白质、脂肪、碳水化合物）
- 🔄 **智能路由**：自动判断输入类型并选择合适的处理流程

## 技术栈

- **框架**: LangGraph 1.0+
- **LLM支持**: OpenAI (GPT-4o), 智谱AI (GLM-4 / GLM-4V-Plus)
- **数据模型**: Pydantic v2

## Getting Started

1. Install dependencies, along with the [LangGraph CLI](https://langchain-ai.github.io/langgraph/concepts/langgraph_cli/), which will be used to run the server.

```bash
cd path/to/your/app
pip install -e . "langgraph-cli[inmem]"
```

2. 配置环境变量。创建 `.env` 文件并添加API密钥：

```bash
# 创建.env文件
touch .env
```

在 `.env` 文件中添加以下配置：

```text
# AI模型配置（可选值: "openai" 或 "zhipu"）
MODEL_NAME=openai

# OpenAI配置（用于文本识别和营养分析）
OPENAI_API_KEY=sk-your-openai-api-key-here

# 智谱AI配置（用于图片识别，必须配置）
ZHIPU_API_KEY=your-zhipu-api-key-here

# LangSmith追踪（可选）
LANGSMITH_API_KEY=lsv2-your-langsmith-api-key-here
```

**注意**：
- 文本识别和营养分析可以使用 OpenAI 或智谱AI
- 图片识别必须使用智谱AI（GLM-4V-Plus模型）

3. Start the LangGraph Server.

```shell
langgraph dev
```

For more information on getting started with LangGraph Server, [see here](https://langchain-ai.github.io/langgraph/tutorials/langgraph-platform/local-server/).

## 使用示例

### 文本食物识别

输入状态示例：
```python
{
    "description": "今天中午吃了一碗牛肉面，还有两个鸡蛋"
}
```

### 图片食物识别

输入状态示例：
```python
{
    "image_url": "https://example.com/food.jpg"
}
```

### 输出结果

系统会自动识别食物并分析营养成分，返回包含以下信息的完整结果：

```python
{
    "food_info": {
        "food_name": "牛肉面配鸡蛋",
        "description": "一碗牛肉面配两个鸡蛋",
        "ingredients": [
            {"name": "牛肉", "quantity": 100.0, "unit": "克"},
            {"name": "面条", "quantity": 200.0, "unit": "克"},
            {"name": "鸡蛋", "quantity": 2.0, "unit": "个"}
        ]
    },
    "nutritional_info": {
        "ingredients": [
            {
                "name": "牛肉",
                "quantity": 100.0,
                "unit": "克",
                "calories": 250.0,
                "protein": 26.0,
                "fat": 15.0,
                "carbohydrates": 0.0
            },
            # ... 更多食材
        ]
    }
}
```

## 工作流程

智能体的工作流程如下：

1. **路由节点**：判断输入类型（文本或图片）
2. **识别节点**：
   - 文本输入 → 使用LLM提取食物信息
   - 图片输入 → 使用视觉模型识别食物
3. **营养分析节点**：基于识别的食物信息，分析详细营养成分
4. **返回结果**：返回完整的食物信息和营养分析结果

## 如何自定义

1. **修改运行时上下文**：在 `graph.py` 中的 `Context` 类可以配置API密钥和模型选择
2. **扩展图结构**：可以在 `graph.py` 中添加新节点、边或修改信息流
3. **调整提示词**：修改各个节点中的提示词模板以优化识别和分析效果

## Development

While iterating on your graph in LangGraph Studio, you can edit past state and rerun your app from previous states to debug specific nodes. Local changes will be automatically applied via hot reload.

Follow-up requests extend the same thread. You can create an entirely new thread, clearing previous history, using the `+` button in the top right.

For more advanced features and examples, refer to the [LangGraph documentation](https://langchain-ai.github.io/langgraph/). These resources can help you adapt this template for your specific use case and build more sophisticated conversational agents.

LangGraph Studio also integrates with [LangSmith](https://smith.langchain.com/) for more in-depth tracing and collaboration with teammates, allowing you to analyze and optimize your chatbot's performance.

