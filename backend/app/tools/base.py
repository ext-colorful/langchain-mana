"""Base Tool class and registry
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from langchain_core.tools import StructuredTool
from pydantic import BaseModel


class ToolParameter(BaseModel):
    """Tool parameter schema"""
    name: str
    type: str  # string, integer, boolean, array, object
    description: str
    required: bool = True
    default: Any | None = None


class ToolMetadata(BaseModel):
    """Tool metadata"""
    name: str
    description: str
    parameters: List[ToolParameter]
    category: str = "general"  # general, data, web, custom
    requires_auth: bool = False
    version: str = "1.0.0"


class BaseTool(ABC):
    """Base class for all tools
    
    Tools must implement:
    - metadata property
    - execute method
    """
    
    @property
    @abstractmethod
    def metadata(self) -> ToolMetadata:
        """Return tool metadata"""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            Tool execution result
        """
        pass
    
    def to_langchain_tool(self) -> StructuredTool:
        """Convert to LangChain StructuredTool
        
        Returns:
            LangChain StructuredTool instance
        """
        return StructuredTool.from_function(
            name=self.metadata.name,
            description=self.metadata.description,
            func=self._sync_wrapper,
            coroutine=self.execute
        )
    
    def _sync_wrapper(self, **kwargs):
        """Synchronous wrapper for execute (required by LangChain)"""
        import asyncio
        return asyncio.run(self.execute(**kwargs))


class ToolRegistry:
    """Central registry for all tools
    Supports dynamic registration and permission control
    """
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._permissions: Dict[str, List[str]] = {}  # tool_name -> [user_ids]
    
    def register(self, tool: BaseTool):
        """Register a new tool"""
        tool_name = tool.metadata.name
        if tool_name in self._tools:
            raise ValueError(f"Tool {tool_name} already registered")
        self._tools[tool_name] = tool
    
    def unregister(self, tool_name: str):
        """Unregister a tool"""
        if tool_name in self._tools:
            del self._tools[tool_name]
    
    def get_tool(self, tool_name: str) -> BaseTool | None:
        """Get a tool by name"""
        return self._tools.get(tool_name)
    
    def list_tools(self, category: str | None = None) -> List[ToolMetadata]:
        """List all registered tools"""
        tools = [tool.metadata for tool in self._tools.values()]
        if category:
            tools = [t for t in tools if t.category == category]
        return tools
    
    def get_tools_for_agent(self, tool_names: List[str]) -> List[StructuredTool]:
        """Get LangChain tools for agent
        
        Args:
            tool_names: List of tool names to retrieve
            
        Returns:
            List of LangChain StructuredTool instances
        """
        tools = []
        for name in tool_names:
            tool = self.get_tool(name)
            if tool:
                tools.append(tool.to_langchain_tool())
        return tools
    
    def check_permission(self, tool_name: str, user_id: str) -> bool:
        """Check if user has permission to use tool
        
        Args:
            tool_name: Name of the tool
            user_id: User ID
            
        Returns:
            True if permitted, False otherwise
        """
        if tool_name not in self._permissions:
            return True  # No restrictions
        return user_id in self._permissions[tool_name]
    
    def grant_permission(self, tool_name: str, user_id: str):
        """Grant tool permission to user"""
        if tool_name not in self._permissions:
            self._permissions[tool_name] = []
        if user_id not in self._permissions[tool_name]:
            self._permissions[tool_name].append(user_id)
    
    def revoke_permission(self, tool_name: str, user_id: str):
        """Revoke tool permission from user"""
        if tool_name in self._permissions and user_id in self._permissions[tool_name]:
            self._permissions[tool_name].remove(user_id)


# Global tool registry
tool_registry = ToolRegistry()
