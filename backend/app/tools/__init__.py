"""Tools module - Tool registry and built-in tools
"""
from .base import BaseTool, ToolMetadata, ToolParameter, tool_registry
from .builtin.calculator import CalculatorTool
from .builtin.weather import WeatherTool


def register_builtin_tools():
    """Register all built-in tools"""
    tool_registry.register(CalculatorTool())
    tool_registry.register(WeatherTool())


__all__ = [
    "BaseTool",
    "ToolMetadata",
    "ToolParameter",
    "tool_registry",
    "register_builtin_tools",
    "CalculatorTool",
    "WeatherTool"
]
