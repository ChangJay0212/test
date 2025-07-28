"""
Abstract base class for tools
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTool(ABC):
    """
    BaseTool class as abstract base class for agent tools.
    Provides interface for creating new tools.
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize tool.
        
        Args:
            name (str): Tool name.
            description (str): Tool description.

        """
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with given parameters.
        
        Args:
            **kwargs: Tool parameters.
            
        Returns:
            Dict[str, Any]: Dictionary containing execution result.

        Raises:
            Exception:
                An error occurred while executing the tool.
        """
        pass
    
    @abstractmethod
    def get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get tool parameters schema for validation.
        
        Returns:
            Dict[str, Any]: JSON schema for tool parameters.
        """
        pass
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """
        Get tool definition for LLM integration.
        
        Returns:
            Dict[str, Any]: Tool definition dictionary.
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.get_parameters_schema()
        }
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate parameters against schema.
        
        Args:
            parameters (Dict[str, Any]): Parameters to validate.
            
        Returns:
            bool: True if parameters are valid, False otherwise.

        Raises:
            Exception:
                An error occurred while validating parameters.
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
