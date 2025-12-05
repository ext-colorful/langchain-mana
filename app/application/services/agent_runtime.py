"""Agent runtime for multi-agent orchestration."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List

from app.core.exceptions import AgentRuntimeError
from app.core.logging import logger
from app.application.services.tool_registry import ToolRegistry


@dataclass
class CancellationToken:
    cancelled: bool = False

    def cancel(self) -> None:
        self.cancelled = True


@dataclass
class AgentContext:
    session_id: str
    user_id: str
    variables: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentDefinition:
    name: str
    handler: Callable[[AgentContext, CancellationToken], Awaitable[Any]]
    tools: List[str] = field(default_factory=list)


class AgentRuntime:
    """Runtime for managing agents, tools, and execution flow."""

    def __init__(self, tool_registry: ToolRegistry | None = None):
        self.agents: Dict[str, AgentDefinition] = {}
        self.tool_registry = tool_registry or ToolRegistry()

    def register_agent(self, agent: AgentDefinition) -> None:
        logger.info(f"Registering agent: {agent.name}")
        self.agents[agent.name] = agent

    def get_agent(self, name: str) -> AgentDefinition:
        if name not in self.agents:
            raise AgentRuntimeError(f"Agent not found: {name}")
        return self.agents[name]

    async def run_serial(
        self, agent_names: List[str], context: AgentContext, token: CancellationToken | None = None
    ) -> List[Any]:
        results = []
        token = token or CancellationToken()
        for name in agent_names:
            if token.cancelled:
                logger.warning("Execution cancelled")
                break
            agent = self.get_agent(name)
            result = await agent.handler(context, token)
            results.append(result)
        return results

    async def run_parallel(
        self, agent_names: List[str], context: AgentContext, token: CancellationToken | None = None
    ) -> List[Any]:
        token = token or CancellationToken()
        tasks = []
        for name in agent_names:
            agent = self.get_agent(name)
            tasks.append(asyncio.create_task(agent.handler(context, token)))
        return await asyncio.gather(*tasks)

    def cancel(self, token: CancellationToken) -> None:
        token.cancel()

    def list_agents(self) -> List[str]:
        return list(self.agents.keys())
