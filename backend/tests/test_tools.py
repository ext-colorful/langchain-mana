"""
Test cases for Tools
"""
import pytest
from app.tools.builtin.calculator import CalculatorTool
from app.tools.builtin.weather import WeatherTool
from app.tools.base import ToolRegistry


@pytest.mark.asyncio
async def test_calculator_tool():
    """Test calculator tool"""
    tool = CalculatorTool()
    
    # Test metadata
    assert tool.metadata.name == "calculator"
    assert len(tool.metadata.parameters) > 0
    
    # Test execution
    result = await tool.execute(expression="2 + 2")
    assert result["result"] == 4
    
    result = await tool.execute(expression="10 * 5")
    assert result["result"] == 50
    
    # Test invalid expression
    result = await tool.execute(expression="invalid")
    assert "error" in result


@pytest.mark.asyncio
async def test_weather_tool():
    """Test weather tool"""
    tool = WeatherTool()
    
    # Test metadata
    assert tool.metadata.name == "weather"
    assert len(tool.metadata.parameters) > 0
    
    # Test execution
    result = await tool.execute(location="Beijing")
    assert result["location"] == "Beijing"
    assert "temperature" in result
    assert "condition" in result
    assert "note" in result  # Mock data note


def test_tool_registry():
    """Test tool registry"""
    registry = ToolRegistry()
    
    # Register tools
    calc_tool = CalculatorTool()
    weather_tool = WeatherTool()
    
    registry.register(calc_tool)
    registry.register(weather_tool)
    
    # List tools
    tools = registry.list_tools()
    assert len(tools) >= 2
    
    # Get tool
    tool = registry.get_tool("calculator")
    assert tool is not None
    assert tool.metadata.name == "calculator"
    
    # Get LangChain tools
    lc_tools = registry.get_tools_for_agent(["calculator", "weather"])
    assert len(lc_tools) == 2


def test_tool_permissions():
    """Test tool permission system"""
    registry = ToolRegistry()
    calc_tool = CalculatorTool()
    registry.register(calc_tool)
    
    # By default, all users have access
    assert registry.check_permission("calculator", "user1")
    
    # Grant specific permission
    registry.grant_permission("calculator", "user1")
    assert registry.check_permission("calculator", "user1")
    
    # Revoke permission
    registry.revoke_permission("calculator", "user1")
    assert not registry.check_permission("calculator", "user1")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
