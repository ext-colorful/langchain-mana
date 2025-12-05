"""Built-in Weather Tool (Mock implementation)
"""
import random
from datetime import datetime
from typing import Any

from ..base import BaseTool, ToolMetadata, ToolParameter


class WeatherTool(BaseTool):
    """Weather query tool (mock implementation)"""
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="weather",
            description="Get current weather information for a location",
            parameters=[
                ToolParameter(
                    name="location",
                    type="string",
                    description="City name or location (e.g., 'Beijing', 'New York')",
                    required=True
                ),
                ToolParameter(
                    name="units",
                    type="string",
                    description="Temperature units: 'celsius' or 'fahrenheit'",
                    required=False,
                    default="celsius"
                )
            ],
            category="web"
        )
    
    async def execute(self, location: str, units: str = "celsius") -> Any:
        """Get weather information (mock data)
        
        Args:
            location: City name
            units: Temperature units
            
        Returns:
            Weather information
        """
        # Mock weather data
        conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy", "Snowy"]
        
        base_temp = random.randint(15, 30)
        temp_c = base_temp
        temp_f = (temp_c * 9/5) + 32
        
        return {
            "location": location,
            "temperature": temp_c if units == "celsius" else temp_f,
            "units": "°C" if units == "celsius" else "°F",
            "condition": random.choice(conditions),
            "humidity": random.randint(40, 80),
            "wind_speed": random.randint(5, 25),
            "timestamp": datetime.utcnow().isoformat(),
            "note": "This is mock weather data for demonstration purposes"
        }
