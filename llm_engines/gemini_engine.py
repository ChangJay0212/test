"""
Gemini LLM Engine implementation with cost monitoring
"""
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from llm_engines.base_engine import BaseLLMEngine
from core.logger import logger
import config.settings as settings
import time


class GeminiEngine(BaseLLMEngine):
    """
    Google Gemini LLM engine implementation
    """
    
    def __init__(self, model_name: str = None, api_key: str = None):
        if model_name is None:
            model_name = settings.GEMINI_MODEL
        if api_key is None:
            api_key = settings.GEMINI_API_KEY
            
        super().__init__(model_name, api_key)
        
        # Cost tracking attributes
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_requests = 0
        self.total_cost = 0.0
        
        # Gemini pricing (as of 2024, in USD per 1K tokens)
        # These should be updated based on current pricing
        self.input_cost_per_1k = 0.0005  # $0.0005 per 1K input tokens
        self.output_cost_per_1k = 0.0015  # $0.0015 per 1K output tokens
        
    def _initialize_client(self):
        """Initialize Gemini client"""
        try:
            if not self.api_key:
                raise ValueError("Gemini API key is required")
                
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model_name)
            logger.info(f"Gemini engine initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate response using Gemini with cost tracking
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
        """
        start_time = time.time()
        
        try:
            # Extract parameters
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 1024)
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            
            # Generate response
            response = self.client.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Calculate costs and tokens
            request_cost = self._calculate_request_cost(prompt, response)
            
            # Update tracking
            self.total_requests += 1
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Log cost information
            logger.info(f"Request cost: ${request_cost['total_cost']:.6f}, "
                       f"Input tokens: {request_cost['input_tokens']}, "
                       f"Output tokens: {request_cost['output_tokens']}, "
                       f"Response time: {response_time:.2f}s")
            
            if response.text:
                logger.debug(f"Generated response: {response.text[:100]}...")
                return response.text
            else:
                logger.warning("Empty response from Gemini")
                return ""
                
        except Exception as e:
            logger.error(f"Error generating response with Gemini: {e}")
            return f"Error: Failed to generate response - {str(e)}"
    
    def generate_with_tools(self, prompt: str, tools: List[Dict[str, Any]], **kwargs) -> str:
        """
        Generate response with tool calling capability
        Note: This is a simplified implementation
        
        Args:
            prompt: Input prompt
            tools: List of available tools
            **kwargs: Additional parameters
            
        Returns:
            Generated response
        """
        try:
            # For this implementation, we'll include tool descriptions in the prompt
            tool_descriptions = self._format_tools_for_prompt(tools)
            
            enhanced_prompt = f"""You are an AI assistant with access to the following tools:

{tool_descriptions}

User request: {prompt}

Please provide a helpful response. If you need to use any tools, mention which tool you would use and why, but focus on providing a direct answer to the user's question."""

            return self.generate_response(enhanced_prompt, **kwargs)
            
        except Exception as e:
            logger.error(f"Error generating response with tools: {e}")
            return f"Error: Failed to generate response with tools - {str(e)}"
    
    def _format_tools_for_prompt(self, tools: List[Dict[str, Any]]) -> str:
        """
        Format tool descriptions for inclusion in prompt
        
        Args:
            tools: List of tool definitions
            
        Returns:
            Formatted tool descriptions
        """
        if not tools:
            return "No additional tools available."
        
        tool_list = []
        for tool in tools:
            name = tool.get('name', 'Unknown')
            description = tool.get('description', 'No description available')
            tool_list.append(f"- {name}: {description}")
        
        return "\n".join(tool_list)
    
    def _calculate_request_cost(self, prompt: str, response) -> Dict[str, Any]:
        """
        Calculate cost for a single request
        
        Args:
            prompt: Input prompt
            response: Gemini response object
            
        Returns:
            Dictionary with cost breakdown
        """
        try:
            # Estimate input tokens (rough approximation: 1 token ≈ 4 characters)
            input_tokens = len(prompt) // 4
            
            # Estimate output tokens
            output_text = response.text if response.text else ""
            output_tokens = len(output_text) // 4
            
            # Calculate costs
            input_cost = (input_tokens / 1000) * self.input_cost_per_1k
            output_cost = (output_tokens / 1000) * self.output_cost_per_1k
            total_cost = input_cost + output_cost
            
            # Update totals
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens
            self.total_cost += total_cost
            
            return {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "input_cost": input_cost,
                "output_cost": output_cost,
                "total_cost": total_cost
            }
            
        except Exception as e:
            logger.error(f"Error calculating request cost: {e}")
            return {
                "input_tokens": 0,
                "output_tokens": 0,
                "input_cost": 0.0,
                "output_cost": 0.0,
                "total_cost": 0.0
            }
    
    def get_cost_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive cost statistics
        
        Returns:
            Dictionary with cost statistics
        """
        return {
            "total_requests": self.total_requests,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost": self.total_cost,
            "average_cost_per_request": self.total_cost / max(self.total_requests, 1),
            "average_tokens_per_request": (self.total_input_tokens + self.total_output_tokens) / max(self.total_requests, 1),
            "input_cost_per_1k": self.input_cost_per_1k,
            "output_cost_per_1k": self.output_cost_per_1k,
            "model_name": self.model_name
        }
    
    def reset_cost_tracking(self):
        """Reset all cost tracking counters"""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_requests = 0
        self.total_cost = 0.0
        logger.info("Cost tracking counters reset")

    def validate_api_key(self) -> bool:
        """
        Validate Gemini API key
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            if not self.api_key:
                return False
            
            # Try a simple API call to validate
            genai.configure(api_key=self.api_key)
            test_model = genai.GenerativeModel('gemini-pro')
            test_response = test_model.generate_content("Hello")
            return test_response is not None
            
        except Exception as e:
            logger.error(f"API key validation failed: {e}")
            return False
