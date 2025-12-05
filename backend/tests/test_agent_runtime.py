"""
Test cases for Agent Runtime
"""
import pytest
from app.agents.runtime import AgentRuntime, AgentContext, CancellationToken


@pytest.mark.asyncio
async def test_agent_context_creation():
    """Test agent context creation"""
    agent_config = {
        "id": 1,
        "model_provider": "openai",
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 2000,
        "system_prompt": "You are a helpful assistant.",
        "tools": ["calculator"],
        "rag_enabled": False,
        "knowledge_base_ids": [],
        "max_iterations": 10,
        "routing_strategy": "cost"
    }
    
    context = AgentContext(
        agent_config=agent_config,
        session_id=1,
        user_id=1
    )
    
    assert context.agent_config["id"] == 1
    assert context.session_id == 1
    assert context.user_id == 1
    assert isinstance(context.cancellation_token, CancellationToken)


@pytest.mark.asyncio
async def test_cancellation_token():
    """Test cancellation token"""
    token = CancellationToken()
    
    assert not token.is_cancelled()
    
    token.cancel()
    
    assert token.is_cancelled()


@pytest.mark.asyncio
async def test_agent_runtime_initialization():
    """Test agent runtime initialization"""
    runtime = AgentRuntime()
    
    assert runtime is not None
    assert len(runtime._active_sessions) == 0


@pytest.mark.asyncio
async def test_session_registration():
    """Test session registration and cancellation"""
    runtime = AgentRuntime()
    
    token = runtime.register_session(1)
    
    assert 1 in runtime._active_sessions
    assert not token.is_cancelled()
    
    runtime.cancel_session(1)
    
    assert token.is_cancelled()
    
    runtime.cleanup_session(1)
    
    assert 1 not in runtime._active_sessions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
