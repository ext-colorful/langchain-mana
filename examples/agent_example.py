"""
Example: Create and run an AI agent with calculator tool and RAG
"""
import asyncio
import os
from pathlib import Path
import sys

# Add backend to path (must be before imports)
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# noqa: E402 - imports after path modification
from app.agents.runtime import AgentRuntime, AgentContext  # noqa: E402
from app.tools import register_builtin_tools  # noqa: E402
from app.rag.pipeline import rag_pipeline  # noqa: E402
from app.storage.chroma_db import chroma_manager  # noqa: E402


async def example_basic_agent():
    """Example 1: Basic agent with calculator tool"""
    print("=" * 60)
    print("Example 1: Basic Agent with Calculator Tool")
    print("=" * 60)
    
    # Register tools
    register_builtin_tools()
    
    # Agent configuration
    agent_config = {
        "id": 1,
        "model_provider": "openai",  # Change based on your API key
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 2000,
        "system_prompt": "You are a helpful AI assistant with access to a calculator.",
        "tools": ["calculator"],
        "rag_enabled": False,
        "knowledge_base_ids": [],
        "max_iterations": 10,
        "routing_strategy": "cost"
    }
    
    # Create agent context
    context = AgentContext(
        agent_config=agent_config,
        session_id=1,
        user_id=1
    )
    
    # Run agent
    runtime = AgentRuntime()
    
    message = "What is 123 multiplied by 456? Please calculate it."
    print(f"\nUser: {message}")
    
    result = await runtime.run(context, message)
    
    if result["success"]:
        print(f"Agent: {result['response']}")
        print(f"\nMetadata: {result['metadata']}")
    else:
        print(f"Error: {result['error']}")


async def example_rag_agent():
    """Example 2: Agent with RAG (knowledge base)"""
    print("\n" + "=" * 60)
    print("Example 2: Agent with RAG Knowledge Base")
    print("=" * 60)
    
    # Register tools
    register_builtin_tools()
    
    # Create a test knowledge base
    namespace = "example_kb"
    
    # Add some sample documents
    print("\n📚 Building knowledge base...")
    sample_text = """
    AI Agent Platform is an enterprise-grade platform for building AI agents.
    
    Key features:
    - Multi-model support (OpenAI, DeepSeek, Qwen, Anthropic)
    - RAG knowledge base with ChromaDB
    - Tool registry with built-in and custom tools
    - Async execution with cancellation support
    - Docker deployment ready
    
    The platform uses FastAPI for the backend and supports streaming responses.
    """
    
    result = await rag_pipeline.ingest_text(
        text=sample_text,
        namespace=namespace,
        metadata={"source": "platform_docs", "type": "documentation"}
    )
    
    if result["success"]:
        print(f"✅ Knowledge base created with {result['total_chunks']} chunks")
    else:
        print(f"❌ Failed to create knowledge base: {result['error']}")
        return
    
    # Agent configuration with RAG enabled
    agent_config = {
        "id": 2,
        "model_provider": "openai",
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 2000,
        "system_prompt": "You are a helpful AI assistant. Use the provided context to answer questions accurately.",
        "tools": [],
        "rag_enabled": True,
        "knowledge_base_ids": [namespace],  # Using namespace directly for demo
        "max_iterations": 10,
        "routing_strategy": "cost"
    }
    
    # Create agent context
    context = AgentContext(
        agent_config=agent_config,
        session_id=2,
        user_id=1
    )
    
    # Run agent with RAG
    runtime = AgentRuntime()
    
    # Query 1
    message = "What are the key features of the AI Agent Platform?"
    print(f"\nUser: {message}")
    
    result = await runtime.run(context, message)
    
    if result["success"]:
        print(f"Agent: {result['response']}")
        if "rag_results" in context.metadata:
            print(f"\n🔍 Retrieved {len(context.metadata['rag_results'])} relevant chunks")
    else:
        print(f"Error: {result['error']}")
    
    # Query 2
    print("\n" + "-" * 60)
    message = "Does the platform support Docker deployment?"
    print(f"\nUser: {message}")
    
    result = await runtime.run(context, message)
    
    if result["success"]:
        print(f"Agent: {result['response']}")
    else:
        print(f"Error: {result['error']}")
    
    # Cleanup
    print("\n🧹 Cleaning up test knowledge base...")
    chroma_manager.delete_collection(namespace)


async def example_multi_tool_agent():
    """Example 3: Agent with multiple tools"""
    print("\n" + "=" * 60)
    print("Example 3: Agent with Multiple Tools")
    print("=" * 60)
    
    # Register tools
    register_builtin_tools()
    
    # Agent configuration with multiple tools
    agent_config = {
        "id": 3,
        "model_provider": "openai",
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 2000,
        "system_prompt": "You are a helpful AI assistant with access to calculator and weather information.",
        "tools": ["calculator", "weather"],
        "rag_enabled": False,
        "knowledge_base_ids": [],
        "max_iterations": 10,
        "routing_strategy": "cost"
    }
    
    # Create agent context
    context = AgentContext(
        agent_config=agent_config,
        session_id=3,
        user_id=1
    )
    
    # Run agent
    runtime = AgentRuntime()
    
    message = "What's the weather in Beijing? Also calculate 25 * 4 for me."
    print(f"\nUser: {message}")
    
    result = await runtime.run(context, message)
    
    if result["success"]:
        print(f"Agent: {result['response']}")
        print(f"\nTools used: {result['metadata'].get('tools_used', [])}")
    else:
        print(f"Error: {result['error']}")


async def main():
    """Run all examples"""
    print("\n🚀 AI Agent Platform - Examples\n")
    
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set!")
        print("Please set your API key in .env file or environment variable.")
        print("\nYou can still run examples with other providers by modifying the agent_config.")
        return
    
    try:
        # Run examples
        await example_basic_agent()
        await asyncio.sleep(1)
        
        await example_rag_agent()
        await asyncio.sleep(1)
        
        await example_multi_tool_agent()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed!")
        print("=" * 60)
    
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(main())
