"""Agent Runtime - Core execution engine for AI agents
"""
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from ..core.config import settings
from ..models.router import RoutingStrategy, model_router
from ..rag.pipeline import rag_pipeline
from ..tools.base import tool_registry
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CancellationToken:
    """Token for cancelling agent execution"""
    
    def __init__(self):
        self._cancelled = False
    
    def cancel(self):
        """Cancel the operation"""
        self._cancelled = True
    
    def is_cancelled(self) -> bool:
        """Check if cancelled"""
        return self._cancelled


class AgentContext:
    """Context for agent execution"""
    
    def __init__(
        self,
        agent_config: Dict[str, Any],
        session_id: int | None = None,
        user_id: int | None = None,
        cancellation_token: CancellationToken | None = None
    ):
        self.agent_config = agent_config
        self.session_id = session_id
        self.user_id = user_id
        self.cancellation_token = cancellation_token or CancellationToken()
        self.metadata = {}
        self.start_time = datetime.utcnow()


class AgentRuntime:
    """Agent Runtime - Manages agent execution lifecycle
    
    Features:
    - Async execution with cancellation support
    - Streaming output
    - Tool integration
    - RAG integration
    - Error handling and retry
    """
    
    def __init__(self):
        self._active_sessions: Dict[int, CancellationToken] = {}
    
    async def run(
        self,
        context: AgentContext,
        message: str,
        chat_history: List | None = None
    ) -> Dict[str, Any]:
        """Run agent synchronously
        
        Args:
            context: Agent execution context
            message: User message
            chat_history: Previous conversation history
            
        Returns:
            Agent response with metadata
        """
        try:
            # Check cancellation
            if context.cancellation_token.is_cancelled():
                raise RuntimeError("Agent execution cancelled")
            
            # Build agent
            agent_executor = await self._build_agent(context)
            
            # Prepare input
            agent_input = await self._prepare_input(context, message)
            
            # Execute
            start_time = datetime.utcnow()
            result = await agent_executor.ainvoke(agent_input)
            end_time = datetime.utcnow()
            
            latency_ms = (end_time - start_time).total_seconds() * 1000
            
            return {
                "success": True,
                "response": result.get("output", ""),
                "metadata": {
                    "agent_id": context.agent_config.get("id"),
                    "session_id": context.session_id,
                    "latency_ms": latency_ms,
                    "model": context.agent_config.get("model_name"),
                    "tools_used": self._extract_tools_used(result),
                    "rag_used": context.agent_config.get("rag_enabled", False)
                }
            }
        
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stream(
        self,
        context: AgentContext,
        message: str,
        chat_history: List | None = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """Run agent with streaming output
        
        Args:
            context: Agent execution context
            message: User message
            chat_history: Previous conversation history
            
        Yields:
            Stream events
        """
        try:
            # Emit start event
            yield {
                "event": "agent_start",
                "data": {
                    "session_id": context.session_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            # Check cancellation
            if context.cancellation_token.is_cancelled():
                raise RuntimeError("Agent execution cancelled")
            
            # Build agent
            agent_executor = await self._build_agent(context)
            
            # Prepare input
            agent_input = await self._prepare_input(context, message)
            
            # Stream execution
            async for event in agent_executor.astream(agent_input):
                if context.cancellation_token.is_cancelled():
                    yield {
                        "event": "agent_cancelled",
                        "data": {"message": "Execution cancelled by user"}
                    }
                    break
                
                # Emit event
                yield {
                    "event": "agent_step",
                    "data": event
                }
            
            # Emit finish event
            yield {
                "event": "agent_finish",
                "data": {
                    "session_id": context.session_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        
        except Exception as e:
            logger.error(f"Agent streaming failed: {e}")
            yield {
                "event": "error",
                "data": {"error": str(e)}
            }
    
    async def _build_agent(self, context: AgentContext) -> AgentExecutor:
        """Build agent executor from configuration"""
        config = context.agent_config
        
        # Get model
        model = model_router.get_model(
            provider=config.get("model_provider"),
            model_name=config.get("model_name"),
            strategy=RoutingStrategy(config.get("routing_strategy", "cost")),
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 2000)
        )
        
        # Get tools
        tool_names = config.get("tools", [])
        tools = tool_registry.get_tools_for_agent(tool_names)
        
        # Build prompt
        system_prompt = config.get("system_prompt", "You are a helpful AI assistant.")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        agent = create_openai_functions_agent(model, tools, prompt)
        
        # Create executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=settings.DEBUG,
            max_iterations=config.get("max_iterations", 10),
            handle_parsing_errors=True
        )
        
        return agent_executor
    
    async def _prepare_input(self, context: AgentContext, message: str) -> Dict[str, Any]:
        """Prepare agent input with RAG context if enabled"""
        agent_input = {"input": message}
        
        # Add RAG context if enabled
        if context.agent_config.get("rag_enabled"):
            kb_ids = context.agent_config.get("knowledge_base_ids", [])
            if kb_ids:
                # Retrieve relevant documents
                namespaces = [f"kb_{kb_id}" for kb_id in kb_ids]
                retrieval_results = rag_pipeline.retrieve(
                    query=message,
                    namespaces=namespaces
                )
                
                if retrieval_results:
                    rag_context = rag_pipeline.build_context(retrieval_results)
                    # Prepend context to message
                    agent_input["input"] = f"{rag_context}\n\nUser Question: {message}"
                    context.metadata["rag_results"] = retrieval_results
        
        return agent_input
    
    def _extract_tools_used(self, result: Dict[str, Any]) -> List[str]:
        """Extract tools used from agent result"""
        tools_used = []
        intermediate_steps = result.get("intermediate_steps", [])
        for step in intermediate_steps:
            if len(step) > 0 and hasattr(step[0], "tool"):
                tools_used.append(step[0].tool)
        return tools_used
    
    def register_session(self, session_id: int) -> CancellationToken:
        """Register a new session"""
        token = CancellationToken()
        self._active_sessions[session_id] = token
        return token
    
    def cancel_session(self, session_id: int):
        """Cancel a running session"""
        if session_id in self._active_sessions:
            self._active_sessions[session_id].cancel()
            logger.info(f"Session {session_id} cancelled")
    
    def cleanup_session(self, session_id: int):
        """Cleanup session after completion"""
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]


# Global agent runtime instance
agent_runtime = AgentRuntime()
