"""Tool registry for agent runtime."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from app.core.logging import logger


class Tool:
    """Represents a callable tool."""

    def __init__(
        self,
        name: str,
        description: str,
        handler: Callable[..., Any],
        permissions: List[str] | None = None,
    ):
        self.name = name
        self.description = description
        self.handler = handler
        self.permissions = permissions or []

    async def execute(self, *args, **kwargs) -> Any:
        return await self.handler(*args, **kwargs)


class ToolRegistry:
    """Registry for managing agent tools."""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        logger.info(f"Registering tool: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Tool not found: {name}")
        return self._tools[name]

    def list_tools(self) -> List[str]:
        return list(self._tools.keys())

    def has_permission(self, tool_name: str, user_permission: str) -> bool:
        tool = self.get(tool_name)
        if not tool.permissions:
            return True
        return user_permission in tool.permissions
