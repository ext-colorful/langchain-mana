"""Built-in Calculator Tool
"""
from typing import Any

from ..base import BaseTool, ToolMetadata, ToolParameter


class CalculatorTool(BaseTool):
    """Simple calculator tool for mathematical operations"""
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="calculator",
            description="Perform mathematical calculations. Supports basic arithmetic operations.",
            parameters=[
                ToolParameter(
                    name="expression",
                    type="string",
                    description="Mathematical expression to evaluate (e.g., '2 + 2', '10 * 5 - 3')",
                    required=True
                )
            ],
            category="general"
        )
    
    async def execute(self, expression: str) -> Any:
        """Execute mathematical expression
        
        Args:
            expression: Math expression to evaluate
            
        Returns:
            Calculation result
        """
        try:
            # Safe evaluation - only allow numbers and basic operators
            allowed_chars = set("0123456789+-*/()., ")
            if not all(c in allowed_chars for c in expression):
                return {"error": "Invalid characters in expression. Only numbers and +, -, *, /, (, ) are allowed."}
            
            result = eval(expression, {"__builtins__": {}}, {})
            return {
                "expression": expression,
                "result": result
            }
        except Exception as e:
            return {
                "error": f"Failed to evaluate expression: {str(e)}",
                "expression": expression
            }
