"""
Weather checking tool for weather information
"""
from typing import Dict, Any
from tools.base_tool import BaseTool
from core.logger import logger


class WeatherCheck(BaseTool):
    """
    Weather tool for getting current weather information
    """
    
    def __init__(self):
        super().__init__(
            name="weather_check",
            description="Get current weather information for a specified location"
        )
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Get weather information for a location
        
        Args:
            location: City name or location to get weather for
            units: Temperature units (metric, imperial, kelvin)
            
        Returns:
            Dictionary with weather information
        """
        try:
            location = kwargs.get('location', 'Unknown')
            units = kwargs.get('units', 'metric')
            
            logger.info(f"Getting weather for: {location}")
            
            # For demo purposes, we'll return simulated weather data
            # In a real implementation, you would use a weather API with your API key
            
            # Simulate weather data based on location
            weather_data = self._get_simulated_weather(location, units)
            
            logger.info(f"Weather data retrieved for {location}")
            
            return {
                "success": True,
                "location": location,
                "weather": weather_data,
                "units": units
            }
            
        except Exception as e:
            error_msg = f"Weather check error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "location": location
            }
    
    def _get_simulated_weather(self, location: str, units: str) -> Dict[str, Any]:
        """
        Generate simulated weather data for demonstration
        
        Args:
            location: Location name
            units: Temperature units
            
        Returns:
            Simulated weather data
        """
        # Simple simulation based on location
        location_lower = location.lower()
        
        if "tokyo" in location_lower:
            temp = 22 if units == "metric" else 72
            condition = "Partly cloudy"
            humidity = 65
            wind_speed = 8
        elif "london" in location_lower:
            temp = 15 if units == "metric" else 59
            condition = "Rainy"
            humidity = 80
            wind_speed = 12
        elif "sydney" in location_lower:
            temp = 25 if units == "metric" else 77
            condition = "Sunny"
            humidity = 60
            wind_speed = 10
        elif "new york" in location_lower or "nyc" in location_lower:
            temp = 18 if units == "metric" else 64
            condition = "Cloudy"
            humidity = 70
            wind_speed = 15
        else:
            # Default weather
            temp = 20 if units == "metric" else 68
            condition = "Clear"
            humidity = 55
            wind_speed = 5
        
        temp_unit = "°C" if units == "metric" else "°F"
        wind_unit = "km/h" if units == "metric" else "mph"
        
        return {
            "temperature": f"{temp}{temp_unit}",
            "condition": condition,
            "humidity": f"{humidity}%",
            "wind_speed": f"{wind_speed} {wind_unit}",
            "description": f"Current weather in {location}: {condition}, {temp}{temp_unit}"
        }
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get tool parameters schema for validation
        
        Returns:
            JSON schema for tool parameters
        """
        return {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name or location to get weather for (e.g., 'Tokyo', 'London', 'New York')"
                },
                "units": {
                    "type": "string",
                    "description": "Temperature units",
                    "enum": ["metric", "imperial", "kelvin"],
                    "default": "metric"
                }
            },
            "required": ["location"]
        }
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get tool schema for function calling
        
        Returns:
            JSON schema for the tool
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name or location to get weather for (e.g., 'Tokyo', 'London', 'New York')"
                        },
                        "units": {
                            "type": "string",
                            "description": "Temperature units",
                            "enum": ["metric", "imperial", "kelvin"],
                            "default": "metric"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    
    def validate_input(self, **kwargs) -> bool:
        """
        Validate input parameters
        
        Returns:
            True if input is valid, False otherwise
        """
        location = kwargs.get('location')
        if not location or not isinstance(location, str):
            logger.error("Weather check requires a valid location")
            return False
        
        units = kwargs.get('units', 'metric')
        if units not in ['metric', 'imperial', 'kelvin']:
            logger.error("Invalid units specified")
            return False
            
        return True
