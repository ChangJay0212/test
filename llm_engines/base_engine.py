"""
Abstract base class for LLM engines
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseLLMEngine(ABC):
    """
    Abstract base class for LLM engines
    Provides interface for different LLM providers
    """
    
    def __init__(self, model_name: str, api_key: str = None):
        """
        Initialize LLM engine
        
        Args:
            model_name: Name/identifier of the model
            api_key: API key for authentication (if required)
        """
        self.model_name = model_name
        self.api_key = api_key
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Initialize the LLM client"""
        pass
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate response from the LLM
        
        Args:
            prompt: Input prompt for the LLM
            **kwargs: Additional parameters for generation
            
        Returns:
            Generated text response
        """
        pass
    
    @abstractmethod
    def generate_with_tools(self, prompt: str, tools: List[Dict[str, Any]], **kwargs) -> str:
        """
        Generate response with tool calling capability
        
        Args:
            prompt: Input prompt for the LLM
            tools: List of available tools
            **kwargs: Additional parameters for generation
            
        Returns:
            Generated response (may include tool calls)
        """
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information
        
        Returns:
            Dictionary containing model metadata
        """
        return {
            "model_name": self.model_name,
            "engine_type": self.__class__.__name__
        }
    
    def validate_api_key(self) -> bool:
        """
        Validate API key if required
        
        Returns:
            True if API key is valid or not required, False otherwise
        """
        # Default implementation - can be overridden by subclasses
        return self.api_key is not None if self.requires_api_key() else True
    
    def requires_api_key(self) -> bool:
        """
        Check if this engine requires an API key
        
        Returns:
            True if API key is required, False otherwise
        """
        return True  # Most LLM services require API keys
