"""Pydantic schemas for Agent-related operations
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class RoutingStrategy(str, Enum):
    """Model routing strategy"""
    COST = "cost"
    SPEED = "speed"
    QUALITY = "quality"
    FALLBACK = "fallback"


class AgentCreate(BaseModel):
    """Schema for creating a new agent"""
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    
    # Model configuration
    model_provider: str = Field(default="openai", description="Model provider: openai, deepseek, qwen, anthropic")
    model_name: str | None = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=1, le=32000)
    
    # Agent settings
    system_prompt: str | None = Field(default="You are a helpful AI assistant.")
    tools: List[str] = Field(default_factory=list, description="List of tool names to enable")
    rag_enabled: bool = Field(default=False)
    knowledge_base_ids: List[int] = Field(default_factory=list)
    
    # Advanced
    max_iterations: int = Field(default=10, ge=1, le=20)
    routing_strategy: RoutingStrategy = Field(default=RoutingStrategy.COST)


class AgentUpdate(BaseModel):
    """Schema for updating an agent"""
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    model_provider: str | None = None
    model_name: str | None = None
    temperature: float | None = Field(None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(None, ge=1, le=32000)
    system_prompt: str | None = None
    tools: List[str] | None = None
    rag_enabled: bool | None = None
    knowledge_base_ids: List[int] | None = None
    max_iterations: int | None = Field(None, ge=1, le=20)
    routing_strategy: RoutingStrategy | None = None
    is_active: bool | None = None


class AgentResponse(BaseModel):
    """Schema for agent response"""
    id: int
    user_id: int
    name: str
    description: str | None
    model_provider: str
    model_name: str | None
    temperature: float
    max_tokens: int
    system_prompt: str | None
    tools: List[str]
    rag_enabled: bool
    knowledge_base_ids: List[int]
    max_iterations: int
    routing_strategy: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None
    
    class Config:
        from_attributes = True


class AgentListResponse(BaseModel):
    """Schema for agent list response"""
    total: int
    agents: List[AgentResponse]


class AgentRunRequest(BaseModel):
    """Schema for running an agent"""
    message: str = Field(..., min_length=1)
    session_id: int | None = None
    stream: bool = Field(default=False)
    metadata: Dict[str, Any] | None = Field(default_factory=dict)


class AgentRunResponse(BaseModel):
    """Schema for agent run response"""
    session_id: int
    message_id: int
    response: str
    metadata: Dict[str, Any] | None = None
    
    # Usage stats
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    # Timing
    latency_ms: float | None = None


class AgentStreamEvent(BaseModel):
    """Schema for streaming events"""
    event_type: str = Field(..., description="agent_start, tool_call, rag_retrieve, chunk, agent_finish, error")
    data: Any
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentStepEvent(BaseModel):
    """Schema for agent execution step"""
    step_type: str  # thinking, tool_call, rag_query, response
    content: Any
    metadata: Dict[str, Any] | None = None
