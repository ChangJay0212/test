"""
Abstract base class for LLM engines
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import time

from src.utils.logger import logger


class BaseLLMEngine(ABC):
    """
    BaseLLMEngine class as abstract base class for LLM engines.
    Provides interface for different LLM providers.
    """
    
    def __init__(self, model_name: str, api_key: str = None):
        """
        Initialize LLM engine.
        
        Args:
            model_name (str): Name/identifier of the model.
            api_key (str, optional): API key for authentication (if required). Defaults to None.

        """
        self.model_name = model_name
        self.api_key = api_key
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """
        Initialize the LLM client.

        """
        pass
    
    @abstractmethod
    def generate_response(self, prompt: str, user_id: str = "anonymous", **kwargs) -> str:
        """
        Generate response from the LLM.
        
        Args:
            prompt (str): Input prompt for the LLM.
            user_id (str): User identifier for cost tracking.
            **kwargs: Additional parameters for generation.
            
        Returns:
            str: Generated text response.

        Raises:
            Exception:
                An error occurred while generating response.
        """
        pass
    
    @abstractmethod
    def generate_with_tools(self, prompt: str, tools: List[Dict[str, Any]], user_id: str = "anonymous", **kwargs) -> str:
        """
        Generate response with tool calling capability.
        
        Args:
            prompt (str): Input prompt for the LLM.
            tools (List[Dict[str, Any]]): List of available tools.
            user_id (str): User identifier for cost tracking.
            **kwargs: Additional parameters for generation.
            
        Returns:
            str: Generated response (may include tool calls).

        Raises:
            Exception:
                An error occurred while generating response with tools.
        """
        pass

    def _send_token_usage_to_cost_monitor(
        self, 
        request_id: str,
        user_id: str,
        agent_uuid: str,
        agent_type: str,
        input_tokens: int,
        output_tokens: int,
        response_time: float,
        success: bool,
        error_message: str = ""
    ):
        """
        Send token usage information to cost monitor via Kafka.
        
        Args:
            request_id: Request identifier
            user_id: User identifier
            agent_uuid: Agent UUID
            agent_type: Agent type
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens  
            response_time: Response time in seconds
            success: Whether the request was successful
            error_message: Error message if any
        """
        try:
            from src.messaging.kafka_client import kafka_client
            import src.config.settings as settings
            
            token_usage_message = {
                "timestamp": time.time(),
                "request_id": request_id,
                "user_id": user_id,
                "agent_uuid": agent_uuid,
                "agent_type": agent_type,
                "model_name": self.model_name,
                "provider": self._get_provider_name(),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "response_time": response_time,
                "success": success,
                "error_message": error_message
            }
            
            # Send to token usage topic
            producer = kafka_client.get_producer()
            producer.send(settings.TOPIC_TOKEN_USAGE, token_usage_message)
            producer.flush()
            
            logger.debug(f"Token usage sent to cost monitor: {input_tokens}+{output_tokens} tokens")
            
        except Exception as e:
            logger.error(f"Failed to send token usage to cost monitor: {e}")

    @abstractmethod
    def _get_provider_name(self) -> str:
        """
        Get the provider name for this engine.
        
        Returns:
            str: Provider name (e.g., "ollama", "gemini", "openai")
        """
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information.
        
        Returns:
            Dict[str, Any]: Dictionary containing model metadata.
        """
        return {
            "model_name": self.model_name,
            "engine_type": self.__class__.__name__,
            "provider": self._get_provider_name()
        }
    
    def validate_api_key(self) -> bool:
        """
        Validate API key if required.
        
        Returns:
            bool: True if API key is valid or not required, False otherwise.
        """
        # Default implementation - can be overridden by subclasses
        return self.api_key is not None if self.requires_api_key() else True
    
    def requires_api_key(self) -> bool:
        """
        Check if this engine requires an API key.
        
        Returns:
            bool: True if API key is required, False otherwise.
        """
        # Default implementation - can be overridden by subclasses
        return False
        return True  # Most LLM services require API keys
