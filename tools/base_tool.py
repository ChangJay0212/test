"""
Abstract base class for tools
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTool(ABC):
    """
    Abstract base class for agent tools
    Provides interface for creating new tools
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize tool
        
        Args:
            name: Tool name
            description: Tool description
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with given parameters
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Dictionary containing execution result
        """
        pass
    
    @abstractmethod
    def get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get tool parameters schema for validation
        
        Returns:
            JSON schema for tool parameters
        """
        pass
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """
        Get tool definition for LLM integration
        
        Returns:
            Tool definition dictionary
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.get_parameters_schema()
        }
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate parameters against schema
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            True if parameters are valid, False otherwise
        """
        try:
            schema = self.get_parameters_schema()
            required_params = schema.get('required', [])
            
            # Check required parameters
            for param in required_params:
                if param not in parameters:
                    return False
            
            # Additional validation can be added here
            return True
            
        except Exception:
            return False
    
    def __str__(self) -> str:
        return f"Tool({self.name}): {self.description}"
